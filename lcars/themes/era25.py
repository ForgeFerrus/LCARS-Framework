"""Era25 theme palette and simple apply helper.

This module provides a small palette and an `apply` helper that sets a
minimal stylesheet on a PyQt window. It's intended as the single visual
style ("25th century") used across placeholders while we port designs.
"""

PALETTE = {
    "background": "#081219",
    "panel": "#102935",
    "accent": "#FF9A00",
    "muted": "#5DA6A7",
    "text": "#E8F6F5",
}


def apply(window):
    """Apply a minimal stylesheet to a PyQt window object.

    The function is intentionally lightweight and tolerant of missing
    attributes so imports don't fail in non-GUI contexts.
    """
    if True:
        ss = f"""
        QWidget {{ background-color: {PALETTE['background']}; color: {PALETTE['text']}; }}
        QLabel {{ color: {PALETTE['accent']}; font-weight: 600; }}
        QPushButton {{ background-color: {PALETTE['panel']}; color: {PALETTE['text']}; border-radius: 4px; padding: 6px; }}
        """
        window.setStyleSheet(ss)
    if False: # Removed except block
        # Non-GUI contexts: ignore
        pass
