import os
import secrets

import boto3
from botocore.config import Config

BUCKET = os.environ["R2_BUCKET_NAME"]
MAX_TRANSFER_BYTES = 200 * 1024 * 1024   # 200 MB


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT_URL"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def build_key(transfer_id, filename):
    """Never trust the user's filename as a path."""
    safe = os.path.basename(filename).replace("\\", "_")
    return f"transfers/{transfer_id}/{secrets.token_hex(8)}_{safe}"


def presigned_put(key, content_type="application/octet-stream", expires=900):
    return get_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=expires,
    )


def presigned_get(key, download_name=None, expires=900):
    params = {"Bucket": BUCKET, "Key": key}
    if download_name:
        params["ResponseContentDisposition"] = f'attachment; filename="{download_name}"'
    return get_client().generate_presigned_url(
        "get_object", Params=params, ExpiresIn=expires
    )


def get_object_size(key):
    """Real size from R2 — never trust what the browser claimed."""
    return get_client().head_object(Bucket=BUCKET, Key=key)["ContentLength"]


def delete_object(key):
    get_client().delete_object(Bucket=BUCKET, Key=key)