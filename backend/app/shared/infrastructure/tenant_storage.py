"""
ModularMenu — Tenant-Aware Storage & Media Isolation (ARC-05 §10, ARC05-D13).
Enforces organization-scoped object storage keys, upload authorization,
and private signed URL verification.
"""

import hashlib
import hmac
import time
from uuid import UUID

from app.shared.application.tenant_context import TenantContext
from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    TenantAccessDeniedException,
)


class TenantStorageManager:
    """
    Manages object keys and access policies for tenant media assets.
    Prevents cross-tenant path traversal and arbitrary bucket reads.
    """

    def __init__(self, signing_secret: str = "modularmenu-storage-test-secret"):
        self._secret = signing_secret.encode("utf-8")

    @staticmethod
    def build_object_key(
        organization_id: UUID,
        category: str,
        filename: str,
        restaurant_id: UUID | None = None,
    ) -> str:
        """
        Constructs a canonical organization-scoped object key.
        Format: media/organizations/{org_id}/restaurants/{restaurant_id}/{category}/{filename}
        """
        # Sanitize filename and category
        clean_cat = category.strip("/").replace("..", "")
        clean_name = filename.strip("/").replace("..", "")
        if restaurant_id:
            return f"media/organizations/{organization_id}/restaurants/{restaurant_id}/{clean_cat}/{clean_name}"
        return f"media/organizations/{organization_id}/{clean_cat}/{clean_name}"

    def validate_key_access(
        self,
        context: TenantContext,
        object_key: str,
    ) -> bool:
        """
        Validates that the given object key belongs strictly to the caller's organization.
        Raises CrossTenantAccessException or TenantAccessDeniedException if invalid.
        """
        parts = object_key.split("/")
        if len(parts) < 3 or parts[0] != "media" or parts[1] != "organizations":
            raise CrossTenantAccessException(f"Invalid storage path structure: {object_key}")

        try:
            key_org_id = UUID(parts[2])
        except ValueError:
            raise CrossTenantAccessException(f"Corrupted tenant identifier in key: {parts[2]}")

        if key_org_id != context.organization_id:
            raise CrossTenantAccessException(
                f"Tenant '{context.organization_id}' attempted to access media of tenant '{key_org_id}'"
            )

        # Check restaurant branch assignment if present
        if len(parts) >= 5 and parts[3] == "restaurants":
            try:
                key_rest_id = UUID(parts[4])
                if not context.has_restaurant_access(key_rest_id):
                    raise TenantAccessDeniedException(
                        f"Context lacks access to restaurant branch '{key_rest_id}' for media"
                    )
            except ValueError:
                pass

        return True

    def generate_signed_url(
        self,
        context: TenantContext,
        object_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        """
        Generates a time-limited HMAC-signed URL after validating tenant ownership.
        """
        self.validate_key_access(context, object_key)
        expiry = int(time.time()) + expires_in_seconds
        payload = f"{object_key}:{expiry}"
        signature = hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"https://cdn.modularmenu.internal/{object_key}?exp={expiry}&sig={signature}"

    def verify_signed_url(self, object_key: str, expiry: int, signature: str) -> bool:
        """Verifies HMAC signature and validity window for signed downloads."""
        if int(time.time()) > expiry:
            return False
        expected_payload = f"{object_key}:{expiry}"
        expected_sig = hmac.new(
            self._secret, expected_payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
