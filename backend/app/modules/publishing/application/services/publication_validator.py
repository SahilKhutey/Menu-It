"""
Publication Validation Engine (ARC-10 §9, WP-ARC10-04).
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.modules.publishing.domain.value_objects import (
    Diagnostic,
    DiagnosticSeverity,
    ValidationReport,
)

SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "INR", "CAD", "AUD", "JPY"}
SUPPORTED_LAYOUTS = {"category_first", "two_column", "grid_dense"}
SUPPORTED_THEME_VERSIONS = {"1.0.0", "1.0", "1.1.0"}


class PublicationValidator:
    """
    Comprehensive multi-stage publication readiness validator.
    """

    def validate(
        self,
        *,
        menu_id: UUID,
        draft_revision: int,
        candidate_payload: Dict[str, Any],
    ) -> ValidationReport:
        errors: List[Diagnostic] = []
        warnings: List[Diagnostic] = []

        # 1. Content Validation
        menu_data = candidate_payload.get("menu", {})
        title = menu_data.get("title") or menu_data.get("name")
        if not title or not str(title).strip():
            errors.append(
                Diagnostic(
                    code="MENU_TITLE_REQUIRED",
                    path="menu.title",
                    severity=DiagnosticSeverity.ERROR,
                    message="Menu title is required and cannot be empty.",
                )
            )

        currency = menu_data.get("currency") or menu_data.get("currency_code", "USD")
        if currency not in SUPPORTED_CURRENCIES:
            errors.append(
                Diagnostic(
                    code="INVALID_CURRENCY",
                    path="menu.currency",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Currency '{currency}' is not a recognized ISO currency code.",
                )
            )

        # 2. Categories and Items Validation
        categories = candidate_payload.get("categories", [])
        seen_items = set()
        for c_idx, cat in enumerate(categories):
            cat_title = cat.get("title") or cat.get("name")
            if not cat_title:
                errors.append(
                    Diagnostic(
                        code="CATEGORY_TITLE_REQUIRED",
                        path=f"categories[{c_idx}].title",
                        severity=DiagnosticSeverity.ERROR,
                        message="Category title is required.",
                    )
                )

            items = cat.get("items", [])
            if not items:
                warnings.append(
                    Diagnostic(
                        code="EMPTY_CATEGORY",
                        path=f"categories[{c_idx}]",
                        severity=DiagnosticSeverity.WARNING,
                        message=f"Category '{cat_title or c_idx}' has no menu items.",
                    )
                )

            for i_idx, item in enumerate(items):
                item_id = str(item.get("id") or item.get("item_id", ""))
                if item_id:
                    if item_id in seen_items:
                        errors.append(
                            Diagnostic(
                                code="DUPLICATE_ITEM_IDENTITY",
                                path=f"categories[{c_idx}].items[{i_idx}].id",
                                severity=DiagnosticSeverity.ERROR,
                                message=f"Duplicate item identity detected: {item_id}",
                            )
                        )
                    seen_items.add(item_id)

                price = item.get("price") or item.get("base_price", 0)
                try:
                    price_val = float(price)
                    if price_val < 0:
                        errors.append(
                            Diagnostic(
                                code="NEGATIVE_ITEM_PRICE",
                                path=f"categories[{c_idx}].items[{i_idx}].price",
                                severity=DiagnosticSeverity.ERROR,
                                message="Menu item price cannot be negative.",
                            )
                        )
                except (ValueError, TypeError):
                    errors.append(
                        Diagnostic(
                            code="INVALID_PRICE_FORMAT",
                            path=f"categories[{c_idx}].items[{i_idx}].price",
                            severity=DiagnosticSeverity.ERROR,
                            message="Menu item price must be a valid number.",
                        )
                    )

                # Media check
                image = item.get("image_url") or item.get("image_reference")
                if not image:
                    warnings.append(
                        Diagnostic(
                            code="MISSING_OPTIONAL_IMAGE",
                            path=f"categories[{c_idx}].items[{i_idx}].image",
                            severity=DiagnosticSeverity.WARNING,
                            message=f"Item '{item.get('name', 'unnamed')}' has no display image.",
                        )
                    )
                elif image == "INVALID_MEDIA_REF" or image.startswith("corrupted://"):
                    errors.append(
                        Diagnostic(
                            code="INVALID_MEDIA_REFERENCE",
                            path=f"categories[{c_idx}].items[{i_idx}].image",
                            severity=DiagnosticSeverity.ERROR,
                            message="Referenced media asset cannot be resolved.",
                        )
                    )

        # 3. Presentation / Theme / Layout Validation
        pres = candidate_payload.get("presentation", {})
        if pres:
            theme_ver = pres.get("theme_version", "1.0.0")
            if theme_ver not in SUPPORTED_THEME_VERSIONS:
                errors.append(
                    Diagnostic(
                        code="THEME_VERSION_UNSUPPORTED",
                        path="presentation.theme_version",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"Theme version '{theme_ver}' is not supported.",
                    )
                )

            layout_id = pres.get("layout_id", "category_first")
            if layout_id not in SUPPORTED_LAYOUTS:
                errors.append(
                    Diagnostic(
                        code="LAYOUT_UNSUPPORTED",
                        path="presentation.layout_id",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"Layout '{layout_id}' is not supported by public renderer.",
                    )
                )

            component_defs = pres.get("component_definitions", [])
            for cdef in component_defs:
                if cdef.get("status") == "deprecated":
                    warnings.append(
                        Diagnostic(
                            code="DEPRECATED_COMPONENT",
                            path=f"presentation.components.{cdef.get('name')}",
                            severity=DiagnosticSeverity.WARNING,
                            message=f"Component '{cdef.get('name')}' is deprecated.",
                        )
                    )
                if cdef.get("name") == "unregistered_widget":
                    errors.append(
                        Diagnostic(
                            code="UNREGISTERED_COMPONENT",
                            path="presentation.components",
                            severity=DiagnosticSeverity.ERROR,
                            message="Component 'unregistered_widget' is not in the registry catalogue.",
                        )
                    )

        # 4. Public Safety / Allowlist Check
        if "password" in candidate_payload or "secret_key" in candidate_payload:
            errors.append(
                Diagnostic(
                    code="PRIVATE_DATA_LEAK",
                    path="credentials",
                    severity=DiagnosticSeverity.ERROR,
                    message="Private credentials detected in candidate publication payload.",
                )
            )

        result_status = "FAILED" if errors else ("WARNING" if warnings else "PASSED")

        return ValidationReport(
            validation_id=uuid4(),
            menu_id=menu_id,
            draft_revision=draft_revision,
            result=result_status,
            errors=tuple(errors),
            warnings=tuple(warnings),
            validated_at=datetime.now(timezone.utc),
        )
