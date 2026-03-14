import time
from typing import Any, Optional

from botocore.exceptions import ClientError

from services._common import build_aws_client, decode_base64_bytes, detect_image_format, get_setting


def _client():
    return build_aws_client("bedrock-runtime", read_timeout=3600)


def _model_id() -> str:
    return get_setting("BEDROCK_MODEL_ID", default="amazon.nova-2-lite-v1:0")


def _converse_with_retry(**kwargs) -> Any:
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays, start=1):
        try:
            return _client().converse(**kwargs)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code not in {
                "ThrottlingException",
                "ServiceUnavailableException",
                "ModelTimeoutException",
                "InternalServerException",
            } or attempt == len(delays):
                raise
            time.sleep(delay)


def _extract_text(response: Any) -> str:
    content = response.get("output", {}).get("message", {}).get("content", [])
    text_parts = [part.get("text", "") for part in content if "text" in part]
    return "\n".join(part for part in text_parts if part).strip()


def call_nova_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    model_id: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    request = {
        "modelId": model_id or _model_id(),
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }

    if system_prompt:
        request["system"] = [{"text": system_prompt}]

    return _extract_text(_converse_with_retry(**request))


def call_nova_multimodal(
    prompt: str,
    image_base64: Any,
    system_prompt: Optional[str] = None,
    model_id: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    image_bytes = decode_base64_bytes(image_base64)
    image_format, _ = detect_image_format(image_bytes)

    request = {
        "modelId": model_id or _model_id(),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": image_format,
                            "source": {"bytes": image_bytes},
                        }
                    },
                    {"text": prompt},
                ],
            }
        ],
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }

    if system_prompt:
        request["system"] = [{"text": system_prompt}]

    return _extract_text(_converse_with_retry(**request))
