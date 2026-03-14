import base64
import io
import time
from typing import Any, Optional

from PIL import Image, ImageOps

from services._common import (
    build_aws_client,
    build_object_key,
    decode_base64_bytes,
    detect_image_format,
    get_setting,
    split_s3_uri,
)
from services.s3 import get_file_url


def _client():
    return build_aws_client("bedrock-runtime", read_timeout=3600)


def _s3_client():
    return build_aws_client("s3")


def _model_id() -> str:
    return get_setting("NOVA_REEL_MODEL_ID", default="amazon.nova-reel-v1:1")


def _output_s3_uri() -> str:
    bucket = get_setting("S3_BUCKET", required=True)
    prefix = get_setting("NOVA_REEL_OUTPUT_PREFIX", default="bedrock/nova-reel")
    clean_prefix = prefix.strip("/")
    if clean_prefix:
        return f"s3://{bucket}/{clean_prefix}/"
    return f"s3://{bucket}/"


def _invocation_output_key(base_prefix: str, invocation_id: str) -> str:
    clean_prefix = base_prefix.strip("/")
    if clean_prefix:
        return f"{clean_prefix}/{invocation_id}/output.mp4"
    return f"{invocation_id}/output.mp4"


def _normalize_image_for_reel(image_input: Any):
    raw_image = decode_base64_bytes(image_input)
    with Image.open(io.BytesIO(raw_image)) as image:
        normalized = ImageOps.fit(image.convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        normalized.save(buffer, format="PNG")
    normalized_bytes = buffer.getvalue()
    return normalized_bytes, base64.b64encode(normalized_bytes).decode("utf-8")


def _build_model_input(prompt: str, duration_seconds: int, image_base64: Optional[Any]) -> dict:
    if duration_seconds % 6 != 0:
        raise ValueError("Nova Reel duration must be a multiple of 6 seconds.")

    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {"text": prompt},
        "videoGenerationConfig": {
            "durationSeconds": duration_seconds,
            "fps": 24,
            "dimension": "1280x720",
            "seed": 42,
        },
    }

    if image_base64:
        raw_image, image_string = _normalize_image_for_reel(image_base64)
        detected_format, _ = detect_image_format(raw_image)

        model_input["textToVideoParams"]["images"] = [
            {
                "format": detected_format,
                "source": {"bytes": image_string},
            }
        ]

    return model_input


def _wait_for_completion(invocation_arn: str, poll_interval_seconds: int, timeout_seconds: int) -> dict:
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        response = _client().get_async_invoke(invocationArn=invocation_arn)
        status = (response.get("status") or "").lower()

        if status == "completed":
            return response

        if status in {"failed", "stopped", "expired"}:
            raise RuntimeError(f"Nova Reel job ended with status: {response.get('status')}")

        time.sleep(poll_interval_seconds)

    raise TimeoutError(f"Nova Reel job timed out after {timeout_seconds} seconds.")


def generate_video(
    image_base64: Any,
    prompt: str,
    duration_seconds: int = 6,
    filename: Optional[str] = None,
    poll_interval_seconds: int = 10,
    timeout_seconds: int = 900,
) -> str:
    output_s3_uri = _output_s3_uri()
    invocation = _client().start_async_invoke(
        modelId=_model_id(),
        modelInput=_build_model_input(prompt, duration_seconds, image_base64),
        outputDataConfig={"s3OutputDataConfig": {"s3Uri": output_s3_uri}},
    )

    invocation_arn = invocation["invocationArn"]
    _wait_for_completion(invocation_arn, poll_interval_seconds, timeout_seconds)

    output_bucket, output_prefix = split_s3_uri(output_s3_uri)
    invocation_id = invocation_arn.rsplit("/", 1)[-1]
    generated_key = _invocation_output_key(output_prefix, invocation_id)
    stable_key = filename or build_object_key("generated/videos", ".mp4")

    _s3_client().copy_object(
        Bucket=output_bucket,
        Key=stable_key,
        CopySource={"Bucket": output_bucket, "Key": generated_key},
        ContentType="video/mp4",
        MetadataDirective="REPLACE",
    )

    return get_file_url(stable_key)
