from typing import Optional

import requests

from services._common import (
    build_aws_client,
    get_bool_setting,
    get_setting,
    guess_content_type,
    parse_s3_reference,
    to_public_s3_url,
)


def _client():
    return build_aws_client("s3")


def _bucket_name() -> str:
    return get_setting("S3_BUCKET", required=True)


def upload_file(file_bytes: bytes, filename: str, content_type: Optional[str] = None) -> str:
    key = filename.lstrip("/").replace("\\", "/")
    extra_args = {
        "ContentType": content_type or guess_content_type(key),
    }

    acl = get_setting("S3_OBJECT_ACL")
    if acl:
        extra_args["ACL"] = acl

    cache_control = get_setting("S3_CACHE_CONTROL")
    if cache_control:
        extra_args["CacheControl"] = cache_control

    _client().put_object(
        Bucket=_bucket_name(),
        Key=key,
        Body=file_bytes,
        **extra_args,
    )
    return get_file_url(key)


def get_file_url(filename: str) -> str:
    if filename.startswith(("http://", "https://")):
        return filename

    bucket = _bucket_name()
    key = filename.lstrip("/").replace("\\", "/")

    if get_bool_setting("S3_USE_PRESIGNED_URL", default=False):
        expires_in = int(get_setting("S3_PRESIGNED_EXPIRES_IN", default=3600))
        return _client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    return to_public_s3_url(bucket, key)


def read_file_bytes(file_reference: str) -> bytes:
    try:
        bucket, key = parse_s3_reference(file_reference)
        response = _client().get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
    except ValueError:
        response = requests.get(file_reference, timeout=120)
        response.raise_for_status()
        return response.content
