import base64
import json
import random
from typing import Optional

from services._common import build_object_key, get_setting
from services.bedrock import _client as _bedrock_client
from services.s3 import upload_file


def _canvas_model_id() -> str:
    return get_setting("NOVA_CANVAS_MODEL_ID", default="amazon.nova-canvas-v1:0")


def _validate_dimensions(width: int, height: int) -> None:
    if width < 320 or height < 320:
        raise ValueError("Nova Canvas images must be at least 320x320.")
    if width > 4096 or height > 4096:
        raise ValueError("Nova Canvas images must be at most 4096x4096.")
    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("Nova Canvas width and height must be divisible by 16.")


def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    quality: str = "standard",
    filename: Optional[str] = None,
) -> str:
    _validate_dimensions(width, height)

    request_body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": quality,
            "width": width,
            "height": height,
            "seed": random.randint(0, 858993459),
            "cfgScale": 8.0,
        },
    }

    response = _bedrock_client().invoke_model(
        modelId=_canvas_model_id(),
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
    )
    response_body = json.loads(response["body"].read())

    if response_body.get("error"):
        raise RuntimeError(f"Nova Canvas failed: {response_body['error']}")

    images = response_body.get("images") or []
    if not images:
        raise RuntimeError("Nova Canvas returned no image data.")

    image_bytes = base64.b64decode(images[0])
    object_key = filename or build_object_key("generated/images", ".png")
    return upload_file(image_bytes, object_key, content_type="image/png")
