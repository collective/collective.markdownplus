from plone.registry.interfaces import IRegistry
from pygments.styles import get_all_styles
from zope.component import getUtility

import re

DEFAULT_PYGMENTS_STYLE = "monokai"
DEFAULT_TERMINAL_BACKGROUND = "#272822"
PYGMENTS_STYLE_NAMES = tuple(sorted(get_all_styles()))
SAFE_CSS_COLOR_RE = re.compile(r"^[#(),.%\-\sa-zA-Z0-9]+$")


def normalize_pygments_style(style_name):
    if style_name in PYGMENTS_STYLE_NAMES:
        return style_name
    return DEFAULT_PYGMENTS_STYLE


def normalize_terminal_background(value):
    value = (value or "").strip()
    if not value:
        return DEFAULT_TERMINAL_BACKGROUND
    if SAFE_CSS_COLOR_RE.match(value):
        return value
    return DEFAULT_TERMINAL_BACKGROUND


def get_markdownplus_settings():
    from collective.markdownplus.interfaces import IMarkdownPlusSettings

    try:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMarkdownPlusSettings,
            prefix="collective.markdownplus",
            check=False,
        )
        return {
            "pygments_style": normalize_pygments_style(
                getattr(settings, "pygments_style", DEFAULT_PYGMENTS_STYLE)
            ),
            "terminal_background": normalize_terminal_background(
                getattr(settings, "terminal_background", DEFAULT_TERMINAL_BACKGROUND)
            ),
        }
    except Exception:
        return {
            "pygments_style": DEFAULT_PYGMENTS_STYLE,
            "terminal_background": DEFAULT_TERMINAL_BACKGROUND,
        }
