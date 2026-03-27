from markdown import Markdown
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import html
import mdx_linkify
import pygments
import pymdownx
import re

_DYNAMIC_MARKDOWN_PACKAGES = (mdx_linkify, pygments, pymdownx)

DEFAULT_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.abbr",
    "markdown.extensions.admonition",
    "markdown.extensions.attr_list",
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.def_list",
    "markdown.extensions.extra",
    "markdown.extensions.footnotes",
    "markdown.extensions.md_in_html",
    "markdown.extensions.meta",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    "markdown.extensions.smarty",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
    "markdown.extensions.wikilinks",
    "mdx_linkify",
    "pymdownx.arithmatex",
    "pymdownx.betterem",
    "pymdownx.caret",
    "pymdownx.critic",
    "pymdownx.details",
    "pymdownx.escapeall",
    "pymdownx.extra",
    "pymdownx.fancylists",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.keys",
    "pymdownx.magiclink",
    "pymdownx.mark",
    "pymdownx.pathconverter",
    "pymdownx.progressbar",
    "pymdownx.quotes",
    "pymdownx.saneheaders",
    "pymdownx.smartsymbols",
    "pymdownx.superfences",
    "pymdownx.tabbed",
    "pymdownx.tasklist",
    "pymdownx.tilde",
]

MERMAID_BLOCK_RE = re.compile(
    r"(?P<fence>^[`~]{3,})[ \t]*mermaid[ \t]*\n(?P<body>.*?)(?:\n(?P=fence)[ \t]*$)",
    re.MULTILINE | re.DOTALL,
)

# Matches <input type="checkbox" ... checked .../> (order of attributes may vary)
_CHECKBOX_CHECKED_RE = re.compile(
    r'<input\s[^>]*type=["\']checkbox["\'][^>]*\bchecked\b[^>]*/?>',
    re.IGNORECASE,
)
# Matches any remaining <input type="checkbox" .../> (unchecked)
_CHECKBOX_UNCHECKED_RE = re.compile(
    r'<input\s[^>]*type=["\']checkbox["\'][^>]*/?>',
    re.IGNORECASE,
)


def get_markdown_extensions():
    """Return markdown extensions configured in registry.

    Falls back to package defaults when the registry is unavailable.
    """

    try:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix="plone")
        return list(settings.markdown_extensions or DEFAULT_MARKDOWN_EXTENSIONS)
    except Exception:
        return list(DEFAULT_MARKDOWN_EXTENSIONS)


def _extract_mermaid_blocks(text):
    replacements = {}

    def repl(match):
        token = f"@@MP_MERMAID_{len(replacements)}@@"
        body = (match.group("body") or "").strip("\n")
        replacements[token] = '<div class="mp-mermaid mermaid">{}</div>'.format(
            html.escape(body)
        )
        return f"\n{token}\n"

    return MERMAID_BLOCK_RE.sub(repl, text or ""), replacements


def _restore_mermaid_blocks(rendered_html, replacements):
    output = rendered_html
    for token, mermaid_html in replacements.items():
        output = output.replace(f"<p>{token}</p>", mermaid_html)
        output = output.replace(token, mermaid_html)
    return output


def _replace_task_checkboxes(rendered_html):
    """Replace <input type="checkbox"> with spans so Plone's safe_html doesn't strip them."""
    out = _CHECKBOX_CHECKED_RE.sub(
        '<span class="task-checkbox task-checkbox-checked" aria-checked="true"></span>',
        rendered_html,
    )
    out = _CHECKBOX_UNCHECKED_RE.sub(
        '<span class="task-checkbox task-checkbox-unchecked" aria-checked="false"></span>',
        out,
    )
    return out


def render_markdown_to_html(text):
    """Render markdown text to HTML with the configured Plone extensions."""

    markdown_input, replacements = _extract_mermaid_blocks(text)

    renderer = Markdown(
        extensions=get_markdown_extensions(),
        extension_configs={
            "pymdownx.highlight": {
                "css_class": "codehilite",
            },
            "pymdownx.arithmatex": {
                "generic": True,
            },
        },
        output_format="html5",
    )
    rendered = renderer.convert(markdown_input)
    rendered = _replace_task_checkboxes(rendered)
    return _restore_mermaid_blocks(rendered, replacements)
