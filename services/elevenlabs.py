from typing import Any, Dict, List, Optional

import requests

from services._common import build_object_key, get_setting
from services.s3 import upload_file


def _api_key() -> str:
    return get_setting("ELEVENLABS_API_KEY", required=True)


def _base_url() -> str:
    return get_setting("ELEVENLABS_BASE_URL", default="https://api.elevenlabs.io")


def generate_voiceover(
    script_text: str,
    voice_id: str,
    model_id: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    url = f"{_base_url()}/v1/text-to-speech/{voice_id}"
    payload = {
        "text": script_text,
        "model_id": model_id or get_setting("ELEVENLABS_MODEL_ID", default="eleven_multilingual_v2"),
        "output_format": get_setting("ELEVENLABS_OUTPUT_FORMAT", default="mp3_44100_128"),
        "voice_settings": {
            "stability": float(get_setting("ELEVENLABS_STABILITY", default=0.45)),
            "similarity_boost": float(get_setting("ELEVENLABS_SIMILARITY_BOOST", default=0.8)),
            "style": float(get_setting("ELEVENLABS_STYLE", default=0.2)),
            "use_speaker_boost": True,
        },
    }

    response = requests.post(
        url,
        headers={
            "xi-api-key": _api_key(),
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=180,
    )
    response.raise_for_status()

    object_key = filename or build_object_key("generated/audio", ".mp3")
    return upload_file(response.content, object_key, content_type="audio/mpeg")


def list_voices() -> List[Dict[str, Any]]:
    response = requests.get(
        f"{_base_url()}/v1/voices",
        headers={"xi-api-key": _api_key()},
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("voices", [])
