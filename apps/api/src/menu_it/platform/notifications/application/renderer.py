"""Notification template loading and autoescaped Jinja2 rendering (FCD-09 WP-03)."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_ROOT = Path(__file__).resolve().parents[1] / "templates"


class TemplateNotFoundError(Exception):
    """Raised when an approved template cannot be found on disk."""


class TemplateRenderer:
    """Safe template renderer enforcing autoescaping and language fallbacks."""

    def __init__(self, root: Path = TEMPLATES_ROOT) -> None:
        self.root = root
        self._html_env = Environment(
            loader=FileSystemLoader(str(root)),
            autoescape=select_autoescape(
                enabled_extensions=("html", "htm", "xml"),
                default_for_string=True,
            ),
        )
        self._text_env = Environment(
            loader=FileSystemLoader(str(root)),
            autoescape=False,
        )

    def _resolve_template_path(
        self,
        channel: str,
        template_id: str,
        filename: str,
        locale: str = "en",
    ) -> str:
        """Resolve localized file path, falling back to 'en' if missing."""
        candidate = Path(channel) / template_id / locale / filename
        if (self.root / candidate).is_file():
            return candidate.as_posix()
        # Locale fallback to English
        fallback = Path(channel) / template_id / "en" / filename
        if (self.root / fallback).is_file():
            return fallback.as_posix()
        # Direct channel / template_id / filename fallback (for in_app)
        direct = Path(channel) / template_id / filename
        if (self.root / direct).is_file():
            return direct.as_posix()
        msg = (
            f"Template '{template_id}/{filename}' not found for '{channel}' and locale '{locale}'."
        )
        raise TemplateNotFoundError(msg)

    def render_email(
        self,
        template_id: str,
        variables: dict[str, str],
        locale: str = "en",
    ) -> tuple[str, str, str]:
        """Render subject, HTML body, and plain-text body for an email template."""
        subject_path = self._resolve_template_path("email", template_id, "subject.txt", locale)
        body_html_path = self._resolve_template_path("email", template_id, "body.html", locale)
        body_txt_path = self._resolve_template_path("email", template_id, "body.txt", locale)

        subject = self._text_env.get_template(subject_path).render(**variables).strip()
        html_body = self._html_env.get_template(body_html_path).render(**variables)
        text_body = self._text_env.get_template(body_txt_path).render(**variables)

        return subject, html_body, text_body

    def render_in_app(
        self,
        template_id: str,
        variables: dict[str, str],
        locale: str = "en",
    ) -> tuple[str, str]:
        """Render title and body text for an in-app notification."""
        title_path = self._resolve_template_path("in_app", template_id, "title.txt", locale)
        body_path = self._resolve_template_path("in_app", template_id, "body.txt", locale)

        title = self._text_env.get_template(title_path).render(**variables).strip()
        body = self._text_env.get_template(body_path).render(**variables).strip()
        return title, body
