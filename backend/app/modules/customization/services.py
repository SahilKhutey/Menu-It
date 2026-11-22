"""
ModularMenu — Customization Application Service (ARC-08 §17.2, §13).
Handles draft persistence, validation, optimistic concurrency, preview generation,
and immutable revision history within authorized tenant scope.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConcurrencyConflictError, ResourceNotFoundError
from app.modules.customization.models import CustomizationRevision, MenuCustomization
from app.modules.customization.registries import get_default_customization_document
from app.modules.customization.resolver import resolve_menu_customization
from app.modules.customization.validators import validator


class CustomizationService:
    """Application service for theme and menu customization."""

    async def get_or_create_customization(
        self, db: AsyncSession, organization_id: uuid.UUID, menu_id: uuid.UUID
    ) -> MenuCustomization:
        """Retrieves or creates initial default customization draft for the menu."""
        stmt = select(MenuCustomization).where(
            MenuCustomization.organization_id == organization_id,
            MenuCustomization.menu_id == menu_id,
        )
        result = await db.execute(stmt)
        record = result.scalars().first()

        if not record:
            default_config = get_default_customization_document()
            record = MenuCustomization(
                organization_id=organization_id,
                menu_id=menu_id,
                revision=1,
                configuration=default_config,
            )
            db.add(record)
            await db.flush()

            # Record initial revision
            rev = CustomizationRevision(
                customization_id=record.id,
                organization_id=organization_id,
                menu_id=menu_id,
                revision=1,
                configuration=default_config,
            )
            db.add(rev)
            await db.commit()
            await db.refresh(record)

        return record

    async def update_customization(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        menu_id: uuid.UUID,
        payload: dict[str, Any],
        expected_revision: int | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> MenuCustomization:
        """Saves validated customization draft with optimistic concurrency check."""
        record = await self.get_or_create_customization(db, organization_id, menu_id)

        # 1. Optimistic Concurrency Check (ARC-08 §13.2)
        if expected_revision is not None and record.revision != expected_revision:
            raise ConcurrencyConflictError(
                f"Concurrency conflict: Draft is at revision {record.revision}, but expected revision was {expected_revision}.",
                current_version=f"revision-{record.revision}",
            )

        # 2. Server-side validation pipeline (ARC-08 §9.3)
        validator.validate(payload)

        # 3. Increment revision and persist
        record.revision += 1
        payload_with_meta = dict(payload)
        payload_with_meta["metadata"] = {
            "revision": record.revision,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        record.configuration = payload_with_meta

        # 4. Immutable revision record (ARC-08 §14.2)
        rev = CustomizationRevision(
            customization_id=record.id,
            organization_id=organization_id,
            menu_id=menu_id,
            revision=record.revision,
            configuration=payload_with_meta,
            created_by=actor_id,
        )
        db.add(rev)
        await db.commit()
        await db.refresh(record)
        return record

    def validate_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Validates customization without persistence."""
        validator.validate(payload)
        return {"valid": True, "errors": [], "warnings": []}

    async def generate_preview(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        menu_id: uuid.UUID,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generates ephemeral preview using the deterministic resolver."""
        if payload is not None:
            validator.validate(payload)
            config = payload
        else:
            record = await self.get_or_create_customization(db, organization_id, menu_id)
            config = record.configuration

        resolved = resolve_menu_customization(config)
        return {
            "menu_id": menu_id,
            "preview": True,
            "resolved_configuration": resolved,
        }

    async def reset_customization(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        menu_id: uuid.UUID,
        theme_id: str = "theme-minimal",
        layout_id: str = "layout-grid",
        actor_id: uuid.UUID | None = None,
    ) -> MenuCustomization:
        """Resets draft configuration back to clean theme/layout defaults."""
        record = await self.get_or_create_customization(db, organization_id, menu_id)
        default_config = get_default_customization_document(theme_id, layout_id)

        record.revision += 1
        default_config["metadata"] = {
            "revision": record.revision,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        record.configuration = default_config

        rev = CustomizationRevision(
            customization_id=record.id,
            organization_id=organization_id,
            menu_id=menu_id,
            revision=record.revision,
            configuration=default_config,
            created_by=actor_id,
        )
        db.add(rev)
        await db.commit()
        await db.refresh(record)
        return record

    async def list_revisions(
        self, db: AsyncSession, organization_id: uuid.UUID, menu_id: uuid.UUID
    ) -> list[CustomizationRevision]:
        """Retrieves historical customization revisions in descending order."""
        stmt = (
            select(CustomizationRevision)
            .where(
                CustomizationRevision.organization_id == organization_id,
                CustomizationRevision.menu_id == menu_id,
            )
            .order_by(desc(CustomizationRevision.revision))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_revision(
        self, db: AsyncSession, organization_id: uuid.UUID, menu_id: uuid.UUID, revision_num: int
    ) -> CustomizationRevision:
        """Retrieves a specific historical revision."""
        stmt = select(CustomizationRevision).where(
            CustomizationRevision.organization_id == organization_id,
            CustomizationRevision.menu_id == menu_id,
            CustomizationRevision.revision == revision_num,
        )
        result = await db.execute(stmt)
        rev = result.scalars().first()
        if not rev:
            raise ResourceNotFoundError(f"Customization revision {revision_num} not found.")
        return rev

    async def restore_revision(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        menu_id: uuid.UUID,
        revision_num: int,
        actor_id: uuid.UUID | None = None,
    ) -> MenuCustomization:
        """Restores a previous revision as a brand new draft revision."""
        rev = await self.get_revision(db, organization_id, menu_id, revision_num)
        record = await self.get_or_create_customization(db, organization_id, menu_id)

        record.revision += 1
        restored_config = dict(rev.configuration)
        restored_config["metadata"] = {
            "revision": record.revision,
            "restored_from": revision_num,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        record.configuration = restored_config

        new_rev = CustomizationRevision(
            customization_id=record.id,
            organization_id=organization_id,
            menu_id=menu_id,
            revision=record.revision,
            configuration=restored_config,
            created_by=actor_id,
        )
        db.add(new_rev)
        await db.commit()
        await db.refresh(record)
        return record


customization_service = CustomizationService()
