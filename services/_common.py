import base64
import mimetypes
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Tuple
from urllib.parse import quote, urlparse

import boto3
from botocore.config import Config

try:
    import streamlit as st
except ImportError:  # pragma: no cover - optional outside Streamlit
    st = None


def get_setting(name: str, default: Any = None, required: bool = False) -> Any:
    value = os.getenv(name)
    if value not in (None, ""):
        return value

    if st is not None:
        try:
            if name in st.secrets:
                secret_value = st.secrets[name]
                if secret_value not in (None, ""):
                    return secret_value
        except Exception:
            pass

    if required and default is None:
        raise RuntimeError(f"Missing required configuration value: {name}")

    return default


def get_bool_setting(name: str, default: bool = False) -> bool:
    value = get_setting(name, default=None)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def build_aws_client(service_name: str, read_timeout: int = 3600):
    region = get_setting("AWS_REGION", default="us-east-1")
    client_kwargs = {
        "region_name": region,
        "config": Config(
            connect_timeout=120,
            read_timeout=read_timeout,
            retries={"max_attempts": 4, "mode": "standard"},
        ),
    }

    access_key = get_setting("AWS_ACCESS_KEY_ID")
    secret_key = get_setting("AWS_SECRET_ACCESS_KEY")
    session_token = get_setting("AWS_SESSION_TOKEN")

    if access_key and secret_key:
        client_kwargs["aws_access_key_id"] = access_key
        client_kwargs["aws_secret_access_key"] = secret_key
        if session_token:
            client_kwargs["aws_session_token"] = session_token

    return boto3.client(service_name, **client_kwargs)


def detect_image_format(image_bytes: bytes) -> Tuple[str, str]:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image/png"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "webp", "image/webp"
    return "jpeg", "image/jpeg"


def decode_base64_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value

    if isinstance(value, str):
        candidate = value.strip()
        if candidate.startswith("data:") and "," in candidate:
            candidate = candidate.split(",", 1)[1]

        padding = (-len(candidate)) % 4
        if padding:
            candidate += "=" * padding

        try:
            return base64.b64decode(candidate)
        except Exception as exc:
            raise ValueError("Expected base64-encoded image data.") from exc

    raise TypeError("Expected image data as bytes or base64 string.")


def encode_base64_bytes(value: Any) -> str:
    raw_bytes = decode_base64_bytes(value)
    return base64.b64encode(raw_bytes).decode("utf-8")


def build_object_key(prefix: str, extension: str) -> str:
    clean_prefix = prefix.strip("/").replace("\\", "/")
    clean_extension = extension if extension.startswith(".") else f".{extension}"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{clean_prefix}/{timestamp}-{uuid.uuid4().hex}{clean_extension}"


def guess_content_type(filename: str, default: str = "application/octet-stream") -> str:
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or default


def split_s3_uri(s3_uri: str) -> Tuple[str, str]:
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Expected an s3:// URI, got: {s3_uri}")

    bucket_and_key = s3_uri[5:]
    bucket, _, key = bucket_and_key.partition("/")
    return bucket, key


def parse_s3_reference(reference: str) -> Tuple[str, str]:
    if reference.startswith("s3://"):
        return split_s3_uri(reference)

    parsed = urlparse(reference)
    if parsed.scheme in {"http", "https"}:
        hostname = parsed.netloc.lower()
        path = parsed.path.lstrip("/")

        if ".s3." in hostname:
            bucket = hostname.split(".s3.", 1)[0]
            return bucket, path

        if hostname.endswith(".s3.amazonaws.com"):
            bucket = hostname[: -len(".s3.amazonaws.com")]
            return bucket, path

        path_parts = path.split("/", 1)
        if hostname == "s3.amazonaws.com" and len(path_parts) == 2:
            return path_parts[0], path_parts[1]

    raise ValueError(f"Could not parse S3 reference: {reference}")


def to_public_s3_url(bucket: str, key: str, region: Optional[str] = None) -> str:
    encoded_key = quote(key.lstrip("/"), safe="/")
    region_name = region or get_setting("AWS_REGION", default="us-east-1")
    if region_name == "us-east-1":
        return f"https://{bucket}.s3.amazonaws.com/{encoded_key}"
    return f"https://{bucket}.s3.{region_name}.amazonaws.com/{encoded_key}"
