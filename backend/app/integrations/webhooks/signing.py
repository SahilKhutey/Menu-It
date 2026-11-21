"""
ModularMenu — Webhook Signing and Verification (ARC-07 §12.3).
Uses HMAC-SHA256 with constant-time comparison and replay protection.
"""
import hashlib
import hmac
import time
from typing import Tuple


def sign_payload(secret: str, timestamp: int, payload_bytes: bytes) -> str:
    """
    Computes hex HMAC-SHA256 signature over `{timestamp}.{payload_bytes}`.
    """
    canonical_data = f"{timestamp}.".encode("utf-8") + payload_bytes
    return hmac.new(secret.encode("utf-8"), canonical_data, hashlib.sha256).hexdigest()


def verify_signature(
    secret: str,
    signature: str,
    timestamp: int,
    payload_bytes: bytes,
    tolerance_seconds: int = 300,
) -> Tuple[bool, str]:
    """
    Validates webhook signature against timestamp and payload using constant-time comparison.
    Rejects timestamps outside tolerance window (replay attack mitigation).
    """
    now = int(time.time())
    if abs(now - timestamp) > tolerance_seconds:
        return False, "Timestamp outside tolerance window (potential replay attack)"

    expected_sig = sign_payload(secret, timestamp, payload_bytes)
    # Strip prefix if present (e.g. 'sha256=...')
    clean_sig = signature.replace("sha256=", "").strip()

    if not hmac.compare_digest(expected_sig, clean_sig):
        return False, "Signature mismatch"

    return True, "Valid signature"
