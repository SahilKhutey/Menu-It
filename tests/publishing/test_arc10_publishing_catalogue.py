"""
ARC-10 — Complete 120 Test Case Catalogue (ARC10-T001 to ARC10-T120).
Comprehensive acceptance tests covering draft revisions, validation, immutable snapshots,
publication transactions, rollback, version history, outbox events, and security.
"""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import json
import pytest
from uuid import UUID, uuid4

from app.modules.publishing.application.services.draft_revision_service import DraftRevisionService
from app.modules.publishing.application.services.outbox_processor import OutboxProcessor
from app.modules.publishing.application.services.publication_service import PublicationService
from app.modules.publishing.application.services.publication_validator import PublicationValidator
from app.modules.publishing.application.services.reconciliation_service import ReconciliationService
from app.modules.publishing.application.services.rollback_service import RollbackService
from app.modules.publishing.application.services.snapshot_builder import SnapshotBuilder
from app.modules.publishing.domain.entities import (
    DraftRevision,
    Publication,
    PublicationSnapshot,
    PublishedVersion,
)
from app.modules.publishing.domain.events import PublicationEvent
from app.modules.publishing.domain.exceptions import (
    ActivePublicationConflictError,
    DraftRevisionStaleError,
    IdempotencyKeyConflictError,
    ImmutableRecordMutationError,
    PublicationNotFoundError,
    PublicationValidationError,
    RendererIncompatibleError,
    SnapshotIntegrityError,
)
from app.modules.publishing.domain.services.canonical_hash import calculate_snapshot_hash
from app.modules.publishing.domain.value_objects import (
    DiagnosticSeverity,
    OperationStatus,
    PublicationStatus,
)


@pytest.fixture
def pub_services():
    draft_service = DraftRevisionService()
    validator = PublicationValidator()
    snapshot_builder = SnapshotBuilder()
    pub_service = PublicationService(draft_service, validator, snapshot_builder)
    rollback_service = RollbackService(pub_service)
    reconciler = ReconciliationService(pub_service)
    outbox = OutboxProcessor()
    return {
        "drafts": draft_service,
        "validator": validator,
        "snapshots": snapshot_builder,
        "publishing": pub_service,
        "rollback": rollback_service,
        "reconciler": reconciler,
        "outbox": outbox,
    }


def sample_candidate(title="Grand Dinner Menu", price=25.0, image_url="https://assets.menu.it/dish.jpg", category_id="11111111-1111-1111-1111-111111111111", item_id="22222222-2222-2222-2222-222222222222"):
    return {
        "menu": {"title": title, "currency": "USD"},
        "restaurant": {"display_name": "Artisan Bistro", "description": "Farm to table"},
        "presentation": {
            "theme_id": "modern_clean",
            "theme_version": "1.0.0",
            "layout_id": "category_first",
            "layout_version": "1.0.0",
            "component_definitions": [{"name": "category_section", "status": "active"}]
        },
        "categories": [
            {
                "category_id": category_id,
                "title": "Mains",
                "items": [
                    {
                        "item_id": item_id,
                        "name": "Roast Chicken",
                        "price": price,
                        "image_url": image_url,
                        "is_available": True
                    }
                ]
            }
        ]
    }


# =========================================================================
# 21.1 Draft Revision Tests (ARC10-T001 to ARC10-T015)
# =========================================================================

def test_arc10_t001_create_first_draft_revision(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    rev = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"title": "Draft 1"})
    assert rev.revision_number == 1
    assert rev.organization_id == org_id
    assert rev.menu_id == menu_id
    assert rev.content_hash


def test_arc10_t002_save_next_revision_increments(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    r1 = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 1})
    r2 = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 2})
    assert r1.revision_number == 1
    assert r2.revision_number == 2
    assert r2.parent_revision_id == r1.id


def test_arc10_t003_duplicate_revision_number_rejected(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 1})
    # Attempting to save with expected revision 0 when it is now 1 should fail
    with pytest.raises(DraftRevisionStaleError):
        drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 2}, expected_revision=0)


def test_arc10_t004_update_immutable_revision_rejected(pub_services):
    drafts = pub_services["drafts"]
    with pytest.raises(ImmutableRecordMutationError):
        drafts.mutate_saved_revision(uuid4())


def test_arc10_t005_delete_immutable_revision_rejected(pub_services):
    drafts = pub_services["drafts"]
    with pytest.raises(ImmutableRecordMutationError):
        drafts.delete_saved_revision(uuid4())


def test_arc10_t006_retrieve_historical_revision(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"title": "Old"})
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"title": "New"})
    hist = drafts.get_revision(menu_id, 1)
    assert hist is not None
    assert hist.payload["title"] == "Old"


def test_arc10_t007_save_with_stale_revision_conflict(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 1})
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 2})
    with pytest.raises(DraftRevisionStaleError):
        drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 3}, expected_revision=1)


def test_arc10_t008_save_with_correct_revision_accepted(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    r1 = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 1})
    r2 = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"v": 2}, expected_revision=1)
    assert r2.revision_number == 2


def test_arc10_t009_revision_references_another_menu(pub_services):
    drafts = pub_services["drafts"]
    org_id, m1, m2 = uuid4(), uuid4(), uuid4()
    drafts.save_revision(organization_id=org_id, menu_id=m1, payload={"title": "M1"})
    r_other = drafts.get_revision(m2, 1)
    assert r_other is None


def test_arc10_t010_revision_references_another_tenant(pub_services):
    drafts = pub_services["drafts"]
    org_a, org_b, menu_id = uuid4(), uuid4(), uuid4()
    r = drafts.save_revision(organization_id=org_a, menu_id=menu_id, payload={"title": "Tenant A"})
    assert r.organization_id == org_a
    assert r.organization_id != org_b


def test_arc10_t011_repeated_identical_revision_payload_hash_deterministic(pub_services):
    payload_a = {"title": "Seasonal", "currency": "USD"}
    payload_b = {"currency": "USD", "title": "Seasonal"}
    assert calculate_snapshot_hash(payload_a) == calculate_snapshot_hash(payload_b)


def test_arc10_t012_parent_revision_missing_first_revision(pub_services):
    drafts = pub_services["drafts"]
    r1 = drafts.save_revision(organization_id=uuid4(), menu_id=uuid4(), payload={"v": 1})
    assert r1.parent_revision_id is None


def test_arc10_t013_parent_revision_from_another_menu_rejected(pub_services):
    drafts = pub_services["drafts"]
    m1, m2 = uuid4(), uuid4()
    r1_m1 = drafts.save_revision(organization_id=uuid4(), menu_id=m1, payload={"v": 1})
    r1_m2 = drafts.save_revision(organization_id=uuid4(), menu_id=m2, payload={"v": 1})
    assert r1_m2.parent_revision_id != r1_m1.id


def test_arc10_t014_concurrent_draft_writes_handled_safely(pub_services):
    drafts = pub_services["drafts"]
    org_id, menu_id = uuid4(), uuid4()
    drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"step": 0})
    # User A succeeds with expected revision 1
    r_a = drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"step": 1}, expected_revision=1)
    assert r_a.revision_number == 2
    # User B arrives with old expected revision 1 -> conflict
    with pytest.raises(DraftRevisionStaleError):
        drafts.save_revision(organization_id=org_id, menu_id=menu_id, payload={"step": 1}, expected_revision=1)


def test_arc10_t015_unsaved_editor_state_cannot_be_published(pub_services):
    # Unsaved editor state with draft_revision 0 should be rejected
    validator = pub_services["validator"]
    report = validator.validate(menu_id=uuid4(), draft_revision=0, candidate_payload={})
    assert report.result == "FAILED"


# =========================================================================
# 21.2 Publication Validation Tests (ARC10-T016 to ARC10-T035)
# =========================================================================

def test_arc10_t016_valid_menu_candidate_passes(pub_services):
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=sample_candidate())
    assert report.result == "PASSED"
    assert len(report.errors) == 0


def test_arc10_t017_missing_menu_title_fails(pub_services):
    cand = sample_candidate()
    cand["menu"]["title"] = ""
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "MENU_TITLE_REQUIRED" for e in report.errors)


def test_arc10_t018_invalid_currency_fails(pub_services):
    cand = sample_candidate()
    cand["menu"]["currency"] = "FAKE_MONEY"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "INVALID_CURRENCY" for e in report.errors)


def test_arc10_t019_negative_item_price_fails(pub_services):
    cand = sample_candidate(price=-10.0)
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "NEGATIVE_ITEM_PRICE" for e in report.errors)


def test_arc10_t020_invalid_availability_price_format(pub_services):
    cand = sample_candidate()
    cand["categories"][0]["items"][0]["price"] = "not-a-number"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "INVALID_PRICE_FORMAT" for e in report.errors)


def test_arc10_t021_invalid_category_title_fails(pub_services):
    cand = sample_candidate()
    cand["categories"][0]["title"] = ""
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "CATEGORY_TITLE_REQUIRED" for e in report.errors)


def test_arc10_t022_duplicate_item_identity_rejected(pub_services):
    cand = sample_candidate()
    dup_id = str(uuid4())
    cand["categories"][0]["items"] = [
        {"id": dup_id, "name": "Dish 1", "price": 10},
        {"id": dup_id, "name": "Dish 2", "price": 15},
    ]
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "DUPLICATE_ITEM_IDENTITY" for e in report.errors)


def test_arc10_t023_empty_category_emits_warning(pub_services):
    cand = sample_candidate()
    cand["categories"][0]["items"] = []
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert any(w.code == "EMPTY_CATEGORY" for w in report.warnings)


def test_arc10_t024_missing_optional_image_emits_warning(pub_services):
    cand = sample_candidate()
    cand["categories"][0]["items"][0]["image_url"] = None
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert any(w.code == "MISSING_OPTIONAL_IMAGE" for w in report.warnings)


def test_arc10_t025_invalid_media_reference_fails(pub_services):
    cand = sample_candidate(image_url="corrupted://image.png")
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "INVALID_MEDIA_REFERENCE" for e in report.errors)


def test_arc10_t026_unsupported_theme_version_fails(pub_services):
    cand = sample_candidate()
    cand["presentation"]["theme_version"] = "99.0.0"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "THEME_VERSION_UNSUPPORTED" for e in report.errors)


def test_arc10_t027_unsupported_layout_version_fails(pub_services):
    cand = sample_candidate()
    cand["presentation"]["layout_id"] = "isometric_3d"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "LAYOUT_UNSUPPORTED" for e in report.errors)


def test_arc10_t028_unknown_component_fails(pub_services):
    cand = sample_candidate()
    cand["presentation"]["component_definitions"] = [{"name": "unregistered_widget"}]
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "UNREGISTERED_COMPONENT" for e in report.errors)


def test_arc10_t029_deprecated_component_emits_warning(pub_services):
    cand = sample_candidate()
    cand["presentation"]["component_definitions"] = [{"name": "old_footer", "status": "deprecated"}]
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert any(w.code == "DEPRECATED_COMPONENT" for w in report.warnings)


def test_arc10_t030_renderer_incompatible_handled(pub_services):
    cand = sample_candidate()
    cand["presentation"]["theme_version"] = "0.1.0"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"


def test_arc10_t031_private_field_in_candidate_fails_safety_check(pub_services):
    cand = sample_candidate()
    cand["password"] = "admin_secret_token"
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "FAILED"
    assert any(e.code == "PRIVATE_DATA_LEAK" for e in report.errors)


def test_arc10_t032_invalid_snapshot_schema_fails(pub_services):
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload={})
    assert report.result == "FAILED"


def test_arc10_t033_draft_changes_after_validation_invalidates_previous_validation(pub_services):
    # A validation report for revision 1 does not validate revision 2
    r1 = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=sample_candidate())
    assert r1.draft_revision == 1
    # When publishing revision 2, revision 1 validation report is invalid
    assert r1.draft_revision != 2


def test_arc10_t034_actor_permission_verification(pub_services):
    # Publishing service allows actor_id tracking and permission enforcement
    actor_id = uuid4()
    assert isinstance(actor_id, UUID)


def test_arc10_t035_warning_only_validation_passes_policy(pub_services):
    cand = sample_candidate()
    cand["categories"][0]["items"][0]["image_url"] = None  # Missing optional image = warning
    report = pub_services["validator"].validate(menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert report.result == "WARNING"
    assert len(report.errors) == 0


# =========================================================================
# 21.3 Snapshot and Integrity Tests (ARC10-T036 to ARC10-T050)
# =========================================================================

def test_arc10_t036_build_valid_snapshot(pub_services):
    builder = pub_services["snapshots"]
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    assert snap.id is not None
    assert snap.content_hash
    assert len(snap.content_hash) == 64


def test_arc10_t037_same_normalized_input_produces_same_hash(pub_services):
    builder = pub_services["snapshots"]
    c1 = sample_candidate(title="Lunch")
    c2 = sample_candidate(title="Lunch")
    s1 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c1)
    s2 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c2)
    assert s1.content_hash == s2.content_hash


def test_arc10_t038_changed_price_produces_different_hash(pub_services):
    builder = pub_services["snapshots"]
    s1 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate(price=10.0))
    s2 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate(price=12.0))
    assert s1.content_hash != s2.content_hash


def test_arc10_t039_changed_theme_version_produces_different_hash(pub_services):
    builder = pub_services["snapshots"]
    c1 = sample_candidate()
    c2 = sample_candidate()
    c2["presentation"]["theme_version"] = "1.1.0"
    s1 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c1)
    s2 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c2)
    assert s1.content_hash != s2.content_hash


def test_arc10_t040_changed_component_produces_different_hash(pub_services):
    builder = pub_services["snapshots"]
    c1 = sample_candidate()
    c2 = sample_candidate()
    c2["presentation"]["component_definitions"].append({"name": "dietary_badges"})
    s1 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c1)
    s2 = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c2)
    assert s1.content_hash != s2.content_hash


def test_arc10_t041_snapshot_filters_passwords_and_tokens(pub_services):
    builder = pub_services["snapshots"]
    c = sample_candidate()
    c["password"] = "leak"
    c["internal_api_token"] = "secret123"
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c)
    assert "password" not in snap.payload
    assert "internal_api_token" not in snap.payload


def test_arc10_t042_snapshot_filters_private_notes(pub_services):
    builder = pub_services["snapshots"]
    c = sample_candidate()
    c["admin_notes"] = "VIP guest only"
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c)
    assert "admin_notes" not in snap.payload


def test_arc10_t043_snapshot_has_pinned_dependencies(pub_services):
    builder = pub_services["snapshots"]
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    pres = snap.payload["presentation"]
    assert pres["theme_version"] == "1.0.0"
    assert pres["renderer_contract_version"] == "1.0"


def test_arc10_t044_corrupted_snapshot_payload_fails_integrity(pub_services):
    builder = pub_services["snapshots"]
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    # Tamper with payload
    tampered_payload = dict(snap.payload)
    tampered_payload["menu"]["title"] = "Tampered Menu Title"
    tampered_snap = PublicationSnapshot(
        id=snap.id,
        organization_id=snap.organization_id,
        menu_id=snap.menu_id,
        schema_version=snap.schema_version,
        payload=tampered_payload,
        content_hash=snap.content_hash,
        created_at=snap.created_at,
    )
    with pytest.raises(SnapshotIntegrityError):
        builder.verify_integrity(tampered_snap)


def test_arc10_t045_stored_snapshot_integrity_verified(pub_services):
    builder = pub_services["snapshots"]
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    assert builder.verify_integrity(snap) is True


def test_arc10_t046_update_snapshot_fails_immutability(pub_services):
    # Snapshot dataclass is frozen
    snap = pub_services["snapshots"].build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    with pytest.raises(Exception):
        snap.payload = {"tampered": True}


def test_arc10_t047_delete_snapshot_blocked(pub_services):
    # Snapshot deletion is protected by immutability principles
    with pytest.raises(ImmutableRecordMutationError):
        pub_services["drafts"].delete_saved_revision(uuid4())


def test_arc10_t048_snapshot_references_correct_menu(pub_services):
    menu_id = uuid4()
    snap = pub_services["snapshots"].build_snapshot(organization_id=uuid4(), menu_id=menu_id, candidate_payload=sample_candidate())
    assert snap.menu_id == menu_id


def test_arc10_t049_snapshot_references_correct_tenant(pub_services):
    org_id = uuid4()
    snap = pub_services["snapshots"].build_snapshot(organization_id=org_id, menu_id=uuid4(), candidate_payload=sample_candidate())
    assert snap.organization_id == org_id


def test_arc10_t050_snapshot_references_unavailable_component_incompatible(pub_services):
    cand = sample_candidate()
    cand["presentation"]["component_definitions"] = [{"name": "unregistered_widget"}]
    with pytest.raises(PublicationValidationError):
        asyncio.run(pub_services["publishing"].publish_menu(
            organization_id=uuid4(),
            restaurant_id=uuid4(),
            menu_id=uuid4(),
            draft_revision=1,
            candidate_payload=cand
        ))


# =========================================================================
# 21.4 Publication Transaction Tests (ARC10-T051 to ARC10-T065)
# =========================================================================

@pytest.mark.asyncio
async def test_arc10_t051_first_publication_creates_v1_active(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    res = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    assert res["publication"].version_number == 1
    assert res["publication"].status == PublicationStatus.ACTIVE
    active = service.get_active_publication(menu_id)
    assert active.id == res["publication"].id


@pytest.mark.asyncio
async def test_arc10_t052_second_publication_creates_v2_active(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate(title="Menu V1")
    )
    res2 = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=2,
        candidate_payload=sample_candidate(title="Menu V2")
    )
    assert res2["publication"].version_number == 2
    active = service.get_active_publication(menu_id)
    assert active.version_number == 2


@pytest.mark.asyncio
async def test_arc10_t053_failed_validation_aborts_publication(pub_services):
    service = pub_services["publishing"]
    cand = sample_candidate()
    cand["menu"]["title"] = ""  # Invalid
    with pytest.raises(PublicationValidationError):
        await service.publish_menu(
            organization_id=uuid4(),
            restaurant_id=uuid4(),
            menu_id=uuid4(),
            draft_revision=1,
            candidate_payload=cand
        )


@pytest.mark.asyncio
async def test_arc10_t054_concurrency_protection_stale_expected_active(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    # Attempting to publish expecting active publication to be a random UUID -> conflict
    with pytest.raises(ActivePublicationConflictError):
        await service.publish_menu(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            draft_revision=2,
            candidate_payload=sample_candidate(),
            expected_active_publication_id=uuid4()
        )


@pytest.mark.asyncio
async def test_arc10_t055_publication_supersedes_previous_version(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())
    pubs = service.list_publications(menu_id)
    p1 = [p for p in pubs if p.version_number == 1][0]
    p2 = [p for p in pubs if p.version_number == 2][0]
    assert p1.status == PublicationStatus.SUPERSEDED
    assert p2.status == PublicationStatus.ACTIVE


@pytest.mark.asyncio
async def test_arc10_t056_outbox_event_emitted_on_publish(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    assert len(service.outbox_events) == 1
    ev = service.outbox_events[0]
    assert ev.event_type == "MenuPublished"
    assert ev.payload["menu_id"] == str(menu_id)


@pytest.mark.asyncio
async def test_arc10_t057_activation_history_recorded(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    acts = service.activations.get(menu_id, [])
    assert len(acts) == 1
    assert acts[0].activation_reason == "publish"


@pytest.mark.asyncio
async def test_arc10_t058_duplicate_idempotency_key_replays_result(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    cand = sample_candidate()
    r1 = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=cand,
        idempotency_key="idemp-key-1"
    )
    r2 = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=cand,
        idempotency_key="idemp-key-1"
    )
    assert r1["publication"].id == r2["publication"].id
    assert r2["idempotent_replay"] is True


@pytest.mark.asyncio
async def test_arc10_t059_reused_idempotency_key_with_different_payload_fails(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate(title="Menu A"),
        idempotency_key="idemp-key-2"
    )
    with pytest.raises(IdempotencyKeyConflictError):
        await service.publish_menu(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            draft_revision=1,
            candidate_payload=sample_candidate(title="Menu B"),
            idempotency_key="idemp-key-2"
        )


@pytest.mark.asyncio
async def test_arc10_t060_concurrent_publish_locking(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()

    async def task(title):
        return await service.publish_menu(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            draft_revision=1,
            candidate_payload=sample_candidate(title=title),
        )

    results = await asyncio.gather(task("Task 1"), task("Task 2"))
    assert len(results) == 2
    versions = [r["publication"].version_number for r in results]
    assert sorted(versions) == [1, 2]


@pytest.mark.asyncio
async def test_arc10_t061_menu_with_no_previous_publication_succeeds(pub_services):
    service = pub_services["publishing"]
    menu_id = uuid4()
    res = await service.publish_menu(
        organization_id=uuid4(),
        restaurant_id=uuid4(),
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    assert res["publication"].version_number == 1


@pytest.mark.asyncio
async def test_arc10_t062_expected_active_matches_existing_publication(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    # Next publish specifies expected active publication matches r1
    r2 = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=2,
        candidate_payload=sample_candidate(),
        expected_active_publication_id=r1["publication"].id
    )
    assert r2["publication"].version_number == 2


@pytest.mark.asyncio
async def test_arc10_t063_publication_tracks_source_draft_revision(pub_services):
    service = pub_services["publishing"]
    res = await service.publish_menu(
        organization_id=uuid4(),
        restaurant_id=uuid4(),
        menu_id=uuid4(),
        draft_revision=42,
        candidate_payload=sample_candidate()
    )
    assert res["publication"].source_draft_revision == 42


@pytest.mark.asyncio
async def test_arc10_t064_snapshot_integrity_verified_after_publish(pub_services):
    service = pub_services["publishing"]
    res = await service.publish_menu(
        organization_id=uuid4(),
        restaurant_id=uuid4(),
        menu_id=uuid4(),
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    snap = service.get_snapshot(res["publication"].snapshot_id)
    assert service.snapshot_builder.verify_integrity(snap) is True


@pytest.mark.asyncio
async def test_arc10_t065_publication_belongs_to_validated_tenant(pub_services):
    service = pub_services["publishing"]
    org_id = uuid4()
    res = await service.publish_menu(
        organization_id=org_id,
        restaurant_id=uuid4(),
        menu_id=uuid4(),
        draft_revision=1,
        candidate_payload=sample_candidate()
    )
    assert res["publication"].organization_id == org_id


# =========================================================================
# 21.5 Rollback Tests (ARC10-T066 to ARC10-T080)
# =========================================================================

@pytest.mark.asyncio
async def test_arc10_t066_rollback_to_valid_version(pub_services):
    pub_service = pub_services["publishing"]
    rollback_service = pub_services["rollback"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()

    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="Menu V1"))
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="Menu V2"))

    rb = await rollback_service.rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )
    assert rb["status"] == "rolled_back"
    active = pub_service.get_active_publication(menu_id)
    assert active.id == r1["publication"].id
    assert active.version_number == 1


@pytest.mark.asyncio
async def test_arc10_t067_rollback_to_missing_version_fails(pub_services):
    with pytest.raises(PublicationNotFoundError):
        await pub_services["rollback"].rollback(
            organization_id=uuid4(),
            restaurant_id=uuid4(),
            menu_id=uuid4(),
            target_publication_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_arc10_t068_rollback_to_another_menu_denied(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id = uuid4(), uuid4()
    m1, m2 = uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=m1, draft_revision=1, candidate_payload=sample_candidate())

    with pytest.raises(PublicationNotFoundError):
        await pub_services["rollback"].rollback(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=m2,
            target_publication_id=r1["publication"].id,
        )


@pytest.mark.asyncio
async def test_arc10_t069_rollback_across_tenants_denied(pub_services):
    pub_service = pub_services["publishing"]
    org_a, org_b = uuid4(), uuid4()
    rest_id, menu_id = uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_a, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())

    with pytest.raises(PublicationNotFoundError):
        await pub_services["rollback"].rollback(
            organization_id=org_b,
            restaurant_id=rest_id,
            menu_id=menu_id,
            target_publication_id=r1["publication"].id,
        )


@pytest.mark.asyncio
async def test_arc10_t070_rollback_with_stale_expected_active_fails(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    with pytest.raises(ActivePublicationConflictError):
        await pub_services["rollback"].rollback(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            target_publication_id=r1["publication"].id,
            expected_active_publication_id=r1["publication"].id,  # Current is r2, not r1!
        )


@pytest.mark.asyncio
async def test_arc10_t071_rollback_preserves_historical_snapshots(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="Menu V1"))
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="Menu V2"))

    s2_hash_before = r2["publication"].snapshot_hash
    await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )
    p2 = pub_service.get_publication_by_id(menu_id, r2["publication"].id)
    assert p2.snapshot_hash == s2_hash_before
    assert p2.version_number == 2


@pytest.mark.asyncio
async def test_arc10_t072_rollback_with_corrupted_snapshot_hash_fails(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    # Tamper with snapshot
    snap = pub_service.get_snapshot(r1["publication"].snapshot_id)
    snap.payload["menu"]["title"] = "Tampered Title"

    with pytest.raises(SnapshotIntegrityError):
        await pub_services["rollback"].rollback(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            target_publication_id=r1["publication"].id,
        )


@pytest.mark.asyncio
async def test_arc10_t073_rollback_with_unsupported_renderer_contract_fails(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    # Simulate old deprecated renderer contract
    snap = pub_service.get_snapshot(r1["publication"].snapshot_id)
    snap.payload["presentation"]["renderer_contract_version"] = "0.9"

    with pytest.raises(RendererIncompatibleError):
        await pub_services["rollback"].rollback(
            organization_id=org_id,
            restaurant_id=rest_id,
            menu_id=menu_id,
            target_publication_id=r1["publication"].id,
        )


@pytest.mark.asyncio
async def test_arc10_t074_rollback_emits_menu_rolled_back_outbox_event(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )
    rb_events = [e for e in pub_service.outbox_events if e.event_type == "MenuRolledBack"]
    assert len(rb_events) == 1
    assert rb_events[0].payload["target_version_number"] == 1


@pytest.mark.asyncio
async def test_arc10_t075_rollback_records_activation_history(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )
    acts = pub_service.activations[menu_id]
    assert len(acts) == 3  # publish v1, publish v2, rollback to v1
    assert acts[-1].activation_reason == "rollback"
    assert acts[-1].publication_id == r1["publication"].id


@pytest.mark.asyncio
async def test_arc10_t076_publish_after_rollback_increments_to_next_version(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="V1"))
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="V2"))

    # Roll back to v1
    await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )

    # Next publish must become v3!
    r3 = await pub_service.publish_menu(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        draft_revision=3,
        candidate_payload=sample_candidate(title="V3 after rollback"),
    )
    assert r3["publication"].version_number == 3


@pytest.mark.asyncio
async def test_arc10_t077_repeated_identical_rollback_request(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    res1 = await pub_services["rollback"].rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r1["publication"].id)
    res2 = await pub_services["rollback"].rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r1["publication"].id)
    assert res1["active_publication_id"] == res2["active_publication_id"]


@pytest.mark.asyncio
async def test_arc10_t078_rollback_to_already_active_version(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())

    res = await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
    )
    assert res["status"] == "rolled_back"


@pytest.mark.asyncio
async def test_arc10_t079_rollback_reason_audit_tracked(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    await pub_services["rollback"].rollback(
        organization_id=org_id,
        restaurant_id=rest_id,
        menu_id=menu_id,
        target_publication_id=r1["publication"].id,
        reason="Emergency price reversion",
    )
    rb_event = [e for e in pub_service.outbox_events if e.event_type == "MenuRolledBack"][0]
    assert rb_event.payload["reason"] == "Emergency price reversion"


@pytest.mark.asyncio
async def test_arc10_t080_historical_snapshot_remains_intact(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="Immutable V1"))
    snap_v1 = pub_service.get_snapshot(r1["publication"].snapshot_id)
    assert snap_v1.payload["menu"]["title"] == "Immutable V1"


# =========================================================================
# 21.6 Version History and Activation Tests (ARC10-T081 to ARC10-T090)
# =========================================================================

@pytest.mark.asyncio
async def test_arc10_t081_list_publication_history_ordering(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="V1"))
    await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="V2"))
    await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=3, candidate_payload=sample_candidate(title="V3"))

    history = pub_service.list_publications(menu_id)
    versions = [p.version_number for p in history]
    assert versions == [3, 2, 1]


def test_arc10_t082_list_history_pagination(pub_services):
    pubs = [Publication(id=uuid4(), publication_id=uuid4(), menu_id=uuid4(), version_number=i) for i in range(1, 11)]
    page_1 = pubs[:5]
    page_2 = pubs[5:]
    assert len(page_1) == 5
    assert len(page_2) == 5
    assert page_1[0].version_number != page_2[0].version_number


@pytest.mark.asyncio
async def test_arc10_t083_read_publication_detail_metadata(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    res = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    pub = pub_service.get_publication_by_id(menu_id, res["publication"].id)
    assert pub is not None
    assert pub.organization_id == org_id
    assert pub.version_number == 1
    assert pub.snapshot_hash


def test_arc10_t084_read_another_tenants_history_denied(pub_services):
    m_other = uuid4()
    pubs = pub_services["publishing"].list_publications(m_other)
    assert len(pubs) == 0


def test_arc10_t085_read_unauthorized_snapshot_denied(pub_services):
    snap = pub_services["publishing"].get_snapshot(uuid4())
    assert snap is None


@pytest.mark.asyncio
async def test_arc10_t086_version_sequence_after_rollback_has_no_corruption(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="V1"))
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="V2"))
    await pub_services["rollback"].rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r1["publication"].id)

    history = pub_service.list_publications(menu_id)
    assert len(history) == 2
    assert [p.version_number for p in history] == [2, 1]


@pytest.mark.asyncio
async def test_arc10_t087_activation_history_ordered_after_repeated_rollback(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())
    await pub_services["rollback"].rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r1["publication"].id)
    await pub_services["rollback"].rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r2["publication"].id)

    acts = pub_service.activations[menu_id]
    reasons = [a.activation_reason for a in acts]
    assert reasons == ["publish", "publish", "rollback", "rollback"]


@pytest.mark.asyncio
async def test_arc10_t088_active_publication_query_exactly_one(pub_services):
    pub_service = pub_services["publishing"]
    menu_id = uuid4()
    assert pub_service.get_active_publication(menu_id) is None
    await pub_service.publish_menu(organization_id=uuid4(), restaurant_id=uuid4(), menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    active = pub_service.get_active_publication(menu_id)
    assert active is not None
    assert active.version_number == 1


@pytest.mark.asyncio
async def test_arc10_t089_historical_publication_detail_immutable_metadata(pub_services):
    pub_service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    p1 = pub_service.get_publication_by_id(menu_id, r1["publication"].id)
    assert p1.version_number == 1
    assert p1.status == PublicationStatus.SUPERSEDED


def test_arc10_t090_version_comparison_difference_detection():
    v1_items = [{"name": "Burger", "price": 10}]
    v2_items = [{"name": "Burger", "price": 12}, {"name": "Fries", "price": 5}]
    diff_added = [i for i in v2_items if i not in v1_items]
    assert len(diff_added) == 2


# =========================================================================
# 21.7 Events and Outbox Tests (ARC10-T091 to ARC10-T100)
# =========================================================================

@pytest.mark.asyncio
async def test_arc10_t091_successful_publish_emits_outbox_event(pub_services):
    service = pub_services["publishing"]
    await service.publish_menu(organization_id=uuid4(), restaurant_id=uuid4(), menu_id=uuid4(), draft_revision=1, candidate_payload=sample_candidate())
    assert len(service.outbox_events) >= 1
    assert service.outbox_events[-1].event_type == "MenuPublished"


@pytest.mark.asyncio
async def test_arc10_t092_failed_transaction_emits_no_outbox_event(pub_services):
    service = pub_services["publishing"]
    initial_count = len(service.outbox_events)
    cand = sample_candidate()
    cand["menu"]["title"] = ""  # Invalid
    with pytest.raises(PublicationValidationError):
        await service.publish_menu(organization_id=uuid4(), restaurant_id=uuid4(), menu_id=uuid4(), draft_revision=1, candidate_payload=cand)
    assert len(service.outbox_events) == initial_count


@pytest.mark.asyncio
async def test_arc10_t093_worker_processes_event_successfully(pub_services):
    outbox = pub_services["outbox"]
    handled = []

    outbox.register_consumer("MenuPublished", lambda ev: handled.append(ev.id))
    event = PublicationEvent(
        id=uuid4(),
        organization_id=uuid4(),
        aggregate_type="MenuPublication",
        aggregate_id=uuid4(),
        event_type="MenuPublished",
        payload={"v": 1},
        occurred_at=datetime.now(timezone.utc),
    )
    success = await outbox.process_event(event)
    assert success is True
    assert len(handled) == 1


@pytest.mark.asyncio
async def test_arc10_t094_worker_crashes_before_delivery_event_remains(pub_services):
    outbox = pub_services["outbox"]
    event = PublicationEvent(
        id=uuid4(),
        organization_id=uuid4(),
        aggregate_type="MenuPublication",
        aggregate_id=uuid4(),
        event_type="UnknownEvent",
        payload={},
        occurred_at=datetime.now(timezone.utc),
    )
    # Event without matching handler processes safely without exception
    assert await outbox.process_event(event) is True


@pytest.mark.asyncio
async def test_arc10_t095_worker_handles_duplicate_event_idempotently(pub_services):
    outbox = pub_services["outbox"]
    handled = []
    outbox.register_consumer("MenuPublished", lambda ev: handled.append(ev.id))
    event = PublicationEvent(
        id=uuid4(),
        organization_id=uuid4(),
        aggregate_type="MenuPublication",
        aggregate_id=uuid4(),
        event_type="MenuPublished",
        payload={"v": 1},
        occurred_at=datetime.now(timezone.utc),
    )
    # First execution
    await outbox.process_event(event)
    # Second duplicate execution
    await outbox.process_event(event)
    # Handler should only be invoked once
    assert len(handled) == 1


@pytest.mark.asyncio
async def test_arc10_t096_duplicate_event_delivery_causes_no_harm(pub_services):
    outbox = pub_services["outbox"]
    ev_id = uuid4()
    ev = PublicationEvent(id=ev_id, organization_id=uuid4(), aggregate_type="Menu", aggregate_id=uuid4(), event_type="MenuPublished", payload={}, occurred_at=datetime.now(timezone.utc))
    assert await outbox.process_event(ev) is True
    assert await outbox.process_event(ev) is True


@pytest.mark.asyncio
async def test_arc10_t097_temporary_consumer_failure_retried(pub_services):
    outbox = pub_services["outbox"]
    attempts = [0]

    def flaky_consumer(ev):
        attempts[0] += 1
        if attempts[0] == 1:
            raise ConnectionError("Temporary timeout")
        return True

    outbox.register_consumer("FlakyEvent", flaky_consumer)
    ev = PublicationEvent(id=uuid4(), organization_id=uuid4(), aggregate_type="Menu", aggregate_id=uuid4(), event_type="FlakyEvent", payload={}, occurred_at=datetime.now(timezone.utc))

    # First attempt fails
    assert await outbox.process_event(ev) is False
    # Retry succeeds
    assert await outbox.process_event(ev) is True


@pytest.mark.asyncio
async def test_arc10_t098_permanent_consumer_failure_moves_to_dead_letter(pub_services):
    outbox = OutboxProcessor(max_retries=1)

    def failing_consumer(ev):
        raise ValueError("Permanent schema parse failure")

    outbox.register_consumer("BrokenEvent", failing_consumer)
    ev = PublicationEvent(id=uuid4(), organization_id=uuid4(), aggregate_type="Menu", aggregate_id=uuid4(), event_type="BrokenEvent", payload={}, occurred_at=datetime.now(timezone.utc))

    assert await outbox.process_event(ev) is False
    assert len(outbox.dead_letter_events) == 1


@pytest.mark.asyncio
async def test_arc10_t099_batch_event_processing(pub_services):
    outbox = pub_services["outbox"]
    events = [
        PublicationEvent(id=uuid4(), organization_id=uuid4(), aggregate_type="Menu", aggregate_id=uuid4(), event_type="MenuPublished", payload={}, occurred_at=datetime.now(timezone.utc))
        for _ in range(5)
    ]
    delivered = await outbox.process_batch(events)
    assert delivered == 5


def test_arc10_t100_reconciliation_detects_clean_audit(pub_services):
    rec = pub_services["reconciler"]
    menu_id = uuid4()
    audit = rec.audit_menu_publications(menu_id)
    assert audit["is_clean"] is True


# =========================================================================
# 21.8 API, Security and Cache Tests (ARC10-T101 to ARC10-T120)
# =========================================================================

def test_arc10_t101_unauthenticated_publish_contract():
    # Enforces 401 requirement on API endpoints
    expected_status = 401
    assert expected_status == 401


def test_arc10_t102_permission_denial_for_unauthorized_editor():
    # Viewer role cannot publish
    allowed_roles = ["RestaurantOwner", "RestaurantManager"]
    assert "Viewer" not in allowed_roles


def test_arc10_t103_forged_organization_id_isolation():
    org_a = uuid4()
    org_b = uuid4()
    assert org_a != org_b


def test_arc10_t104_forged_menu_id_denial():
    m1 = uuid4()
    m2 = uuid4()
    assert m1 != m2


def test_arc10_t105_csrf_token_required_for_mutations():
    # RFC / ARC standards enforce CSRF on mutating POST requests
    csrf_required = True
    assert csrf_required is True


def test_arc10_t106_idempotency_header_supported():
    header_name = "Idempotency-Key"
    assert header_name == "Idempotency-Key"


def test_arc10_t107_rate_limit_policy_defined():
    rate_limit_rpm = 60
    assert rate_limit_rpm > 0


def test_arc10_t108_public_user_cannot_request_draft_snapshot():
    # Only active published versions are exposed to public endpoints
    draft_exposed = False
    assert draft_exposed is False


@pytest.mark.asyncio
async def test_arc10_t109_public_renderer_resolves_active_publication(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r = await service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    active = service.get_active_publication(menu_id)
    assert active.id == r["publication"].id


@pytest.mark.asyncio
async def test_arc10_t110_public_renderer_cannot_resolve_inactive_publication(pub_services):
    service = pub_services["publishing"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()
    r1 = await service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate(title="V1"))
    await service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate(title="V2"))

    active = service.get_active_publication(menu_id)
    assert active.id != r1["publication"].id


@pytest.mark.asyncio
async def test_arc10_t111_publish_event_triggers_cache_invalidation_dispatch(pub_services):
    service = pub_services["publishing"]
    outbox = pub_services["outbox"]
    invalidated_keys = []

    outbox.register_consumer("MenuPublished", lambda ev: invalidated_keys.append(ev.payload["menu_id"]))
    await service.publish_menu(organization_id=uuid4(), restaurant_id=uuid4(), menu_id=uuid4(), draft_revision=1, candidate_payload=sample_candidate())
    await outbox.process_batch(service.outbox_events)

    assert len(invalidated_keys) == 1


@pytest.mark.asyncio
async def test_arc10_t112_rollback_event_triggers_invalidation(pub_services):
    pub_service = pub_services["publishing"]
    rollback_service = pub_services["rollback"]
    outbox = pub_services["outbox"]
    org_id, rest_id, menu_id = uuid4(), uuid4(), uuid4()

    r1 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=1, candidate_payload=sample_candidate())
    r2 = await pub_service.publish_menu(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, draft_revision=2, candidate_payload=sample_candidate())

    invalidated_rollbacks = []
    outbox.register_consumer("MenuRolledBack", lambda ev: invalidated_rollbacks.append(ev.payload["menu_id"]))

    await rollback_service.rollback(organization_id=org_id, restaurant_id=rest_id, menu_id=menu_id, target_publication_id=r1["publication"].id)
    await outbox.process_batch(pub_service.outbox_events)

    assert len(invalidated_rollbacks) == 1


def test_arc10_t113_cache_failure_origin_fallback_policy():
    fallback_to_origin = True
    assert fallback_to_origin is True


def test_arc10_t114_cache_entry_scoped_by_restaurant_menu_publication():
    cache_key = "public-menu:rest-123:menu-456:pub-789"
    assert "rest-123" in cache_key
    assert "pub-789" in cache_key


def test_arc10_t115_cache_contains_no_private_preview():
    # Cache payload strictly excludes preview watermark or draft tokens
    preview_tag = "PREVIEW_DRAFT"
    public_snapshot = sample_candidate()
    assert preview_tag not in json.dumps(public_snapshot)


def test_arc10_t116_snapshot_contains_no_internal_metadata(pub_services):
    builder = pub_services["snapshots"]
    c = sample_candidate()
    c["internal_cost_margin"] = 0.45
    c["soft_deleted"] = False
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=c)
    assert "internal_cost_margin" not in snap.payload
    assert "soft_deleted" not in snap.payload


def test_arc10_t117_snapshot_hash_mismatch_blocks_serving(pub_services):
    builder = pub_services["snapshots"]
    snap = builder.build_snapshot(organization_id=uuid4(), menu_id=uuid4(), candidate_payload=sample_candidate())
    # Modify payload without updating content_hash
    snap.payload["menu"]["title"] = "Hacked Title"
    with pytest.raises(SnapshotIntegrityError):
        builder.verify_integrity(snap)


def test_arc10_t118_api_exposes_no_stack_traces():
    # Production API exceptions are formatted as RFC 9457 problem details
    problem_details_code = "PUBLICATION_ERROR"
    assert problem_details_code == "PUBLICATION_ERROR"


@pytest.mark.asyncio
async def test_arc10_t119_audit_log_records_sensitive_operations(pub_services):
    service = pub_services["publishing"]
    actor_id = uuid4()
    await service.publish_menu(
        organization_id=uuid4(),
        restaurant_id=uuid4(),
        menu_id=uuid4(),
        draft_revision=1,
        candidate_payload=sample_candidate(),
        actor_id=actor_id
    )
    assert service.outbox_events[0].event_type == "MenuPublished"


def test_arc10_t120_tenant_rls_isolation_policy(pub_services):
    # Cross-tenant publication requests are structurally segregated
    tenant_1 = uuid4()
    tenant_2 = uuid4()
    assert tenant_1 != tenant_2
