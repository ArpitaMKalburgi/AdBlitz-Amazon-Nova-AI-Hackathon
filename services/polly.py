from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError

from services._common import build_aws_client, build_object_key, get_setting
from services.s3 import upload_file


def _client():
    return build_aws_client("polly")


def _engine() -> str:
    return get_setting("POLLY_ENGINE", default="neural")


def _language_code() -> str:
    return get_setting("POLLY_LANGUAGE_CODE", default="en-US")


def _sample_rate() -> str:
    return str(get_setting("POLLY_SAMPLE_RATE", default="24000"))


def _configured_voice() -> List[Dict[str, Any]]:
    voice_id = get_setting("POLLY_VOICE_ID", default=get_setting("ELEVENLABS_VOICE_ID", default=""))
    if not voice_id:
        return []

    return [
        {
            "voice_id": voice_id,
            "name": voice_id,
            "labels": {
                "gender": "",
                "language_code": _language_code(),
                "language_name": _language_code(),
                "engines": [_engine()],
            },
            "description": f"Configured Polly voice {voice_id}",
        }
    ]


def generate_voiceover(
    script_text: str,
    voice_id: str,
    model_id: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    del model_id

    response = _client().synthesize_speech(
        Engine=_engine(),
        LanguageCode=_language_code(),
        OutputFormat="mp3",
        SampleRate=_sample_rate(),
        Text=script_text,
        TextType="text",
        VoiceId=voice_id,
    )

    audio_stream = response.get("AudioStream")
    if audio_stream is None:
        raise RuntimeError("Amazon Polly did not return an audio stream.")

    object_key = filename or build_object_key("generated/audio", ".mp3")
    return upload_file(audio_stream.read(), object_key, content_type="audio/mpeg")


def list_voices() -> List[Dict[str, Any]]:
    voices: List[Dict[str, Any]] = []
    client = _client()
    next_token = None

    while True:
        params = {
            "Engine": _engine(),
            "LanguageCode": _language_code(),
            "IncludeAdditionalLanguageCodes": True,
        }
        if next_token:
            params["NextToken"] = next_token

        try:
            response = client.describe_voices(**params)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code == "AccessDeniedException":
                return _configured_voice()
            raise
        for voice in response.get("Voices", []):
            voices.append(
                {
                    "voice_id": voice.get("Id"),
                    "name": voice.get("Name"),
                    "labels": {
                        "gender": voice.get("Gender", ""),
                        "language_code": voice.get("LanguageCode", ""),
                        "language_name": voice.get("LanguageName", ""),
                        "engines": voice.get("SupportedEngines", []),
                    },
                    "description": f"{voice.get('Gender', '')} {voice.get('LanguageName', '')} voice".strip(),
                }
            )

        next_token = response.get("NextToken")
        if not next_token:
            break

    return voices
