"""Unit tests for notification template rendering and autoescaping (FCD-09 WP-03)."""

import pytest

from menu_it.platform.notifications.application.renderer import (
    TemplateNotFoundError,
    TemplateRenderer,
)


def test_render_email_account_welcome_en():
    """Renders English welcome email template with escaped variables."""
    renderer = TemplateRenderer()
    subject, html_body, text_body = renderer.render_email(
        template_id="account-welcome",
        variables={"app_name": "Menu-It", "user_name": "Alice <script>alert(1)</script>"},
        locale="en",
    )

    assert "Welcome to Menu-It" in subject
    assert "Alice" in subject
    # Verify autoescaping: <script> becomes &lt;script&gt;
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_body
    assert "<script>" not in html_body
    # Text body has raw text
    assert "Alice <script>alert(1)</script>" in text_body


def test_render_email_account_welcome_hi():
    """Renders Hindi welcome email template."""
    renderer = TemplateRenderer()
    subject, html_body, text_body = renderer.render_email(
        template_id="account-welcome",
        variables={"app_name": "Menu-It", "user_name": "राहुल"},
        locale="hi",
    )

    assert "स्वागत है" in subject
    assert "राहुल" in subject
    assert "नमस्ते राहुल" in text_body


def test_render_email_locale_fallback():
    """Unsupported locale falls back gracefully to English."""
    renderer = TemplateRenderer()
    subject, _, _ = renderer.render_email(
        template_id="account-welcome",
        variables={"app_name": "Menu-It", "user_name": "Pierre"},
        locale="fr",  # Not provided, should fallback to 'en'
    )
    assert subject == "Welcome to Menu-It, Pierre!"


def test_render_in_app_order_status():
    """Renders in-app notification title and body."""
    renderer = TemplateRenderer()
    title, body = renderer.render_in_app(
        template_id="order-status",
        variables={"order_number": "1042", "status_label": "Ready for Pickup"},
    )
    assert title == "Order #1042 Updated"
    assert body == "Your order #1042 is now Ready for Pickup."


def test_render_missing_template_raises():
    """Non-existent template raises TemplateNotFoundError."""
    renderer = TemplateRenderer()
    with pytest.raises(TemplateNotFoundError):
        renderer.render_email(
            template_id="unknown-template-xyz",
            variables={},
        )
