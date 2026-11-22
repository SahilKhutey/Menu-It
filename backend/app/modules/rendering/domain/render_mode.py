"""
Render Mode Definitions (ARC-09 §3, WP-ARC09-02).
"""
from enum import Enum


class RenderMode(str, Enum):
    """
    Identifies the context and security boundary for a rendering pass.
    """
    PUBLIC_PUBLISHED = "public_published"
    DRAFT_PREVIEW = "draft_preview"
    LOCAL_EDITOR = "local_editor"
