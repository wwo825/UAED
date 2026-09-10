import os

import boto3
from dotenv import load_dotenv

load_dotenv()

CF_R2_ACCESS_KEY = os.getenv("CF_R2_ACCESS_KEY_ID")
CF_R2_SECRET_KEY = os.getenv("CF_R2_SECRET_ACCESS_KEY")
CF_R2_ENDPOINT_URL = os.getenv("CF_R2_ENDPOINT_URL")
BUCKET_NAME = os.getenv("CF_R2_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=CF_R2_ENDPOINT_URL,
    aws_access_key_id=CF_R2_ACCESS_KEY,
    aws_secret_access_key=CF_R2_SECRET_KEY,
    region_name="auto",
)

r2_prefix = "haraj"
LOCAL_ROOT = r2_prefix

PREFIXES = [
    f"{r2_prefix}/",
]

MONITOR_STATUS_FILE = f"{r2_prefix}/monitor/monitor_stats.yml"
MONITOR_CONFIG_FILE = f"{r2_prefix}/monitor/websites-config.yml"


def list_all_objects(prefix):
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=prefix,
    ):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def download_file(key):
    # Skip images
    if "/images/" in key:
        return False

    local_path = os.path.join(LOCAL_ROOT, key)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    print(f"⬇ {key}")

    s3.download_file(
        BUCKET_NAME,
        key,
        local_path,
    )

    return True


def main():
    downloaded = 0
    skipped = 0
    failed = 0

    for prefix in PREFIXES:
        print(f"\nSearching under: {prefix}")

        for key in list_all_objects(prefix):

            # Skip folder keys
            if key.endswith("/"):
                continue

            # Skip images
            if "/images/" in key:
                skipped += 1
                continue

            try:
                if download_file(key):
                    downloaded += 1

            except Exception as e:
                failed += 1
                print(f"❌ {key}")
                print(e)

    print("\n==============================")
    print(f"Downloaded : {downloaded}")
    print(f"Skipped    : {skipped} (images)")
    print(f"Failed     : {failed}")
    print("==============================")


if __name__ == "__main__":
    main()