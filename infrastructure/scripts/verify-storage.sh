#!/usr/bin/env bash
# ModularMenu — Object Storage Adapter Verification (ARC-11 §10)
set -euo pipefail

STORAGE_BACKEND="${STORAGE_BACKEND:-local}"
LOCAL_PATH="${LOCAL_STORAGE_PATH:-/app/storage}"

echo "=== Verifying Object Storage Configuration (Backend: $STORAGE_BACKEND) ==="

if [ "$STORAGE_BACKEND" = "local" ]; then
    if [ ! -d "$LOCAL_PATH" ]; then
        echo "Creating local storage directory: $LOCAL_PATH"
        mkdir -p "$LOCAL_PATH"
    fi
    TEST_FILE="$LOCAL_PATH/.storage_write_test"
    touch "$TEST_FILE" && rm "$TEST_FILE"
    echo "✓ Local storage directory is writable: $LOCAL_PATH"
elif [ "$STORAGE_BACKEND" = "s3" ]; then
    : "${S3_ENDPOINT_URL:?S3_ENDPOINT_URL must be set when STORAGE_BACKEND=s3}"
    : "${S3_BUCKET_NAME:?S3_BUCKET_NAME must be set when STORAGE_BACKEND=s3}"
    echo "✓ S3 configuration parameters present: Bucket=$S3_BUCKET_NAME Endpoint=$S3_ENDPOINT_URL"
else
    echo "ERROR: Unsupported STORAGE_BACKEND: $STORAGE_BACKEND"
    exit 1
fi

echo "=== Object Storage Verification Completed ==="
