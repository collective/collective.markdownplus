from collective.markdownplus.settings import get_markdownplus_settings

import html
import importlib

ViewletBase = importlib.import_module("plone.app.layout.viewlets.common").ViewletBase
getSite = importlib.import_module("zope.component.hooks").getSite


class MarkdownAssetsViewlet(ViewletBase):
    """Inject markdownplus CSS and JS for classic UI forms."""

    index = None

    def render(self):
        portal = getSite()
        portal_url = portal.absolute_url()
        settings = get_markdownplus_settings()
        pygments_style = settings["pygments_style"]
        terminal_background = html.escape(
            settings["terminal_background"],
            quote=True,
        )
        return "".join(
            [
                '<link rel="stylesheet" href="{}/++resource++collective.markdownplus/vendor/easymde/easymde.min.css" />'.format(
                    portal_url
                ),
                '<link rel="stylesheet" href="{}/++resource++collective.markdownplus/pygments/{}.css" />'.format(
                    portal_url,
                    pygments_style,
                ),
                '<link rel="stylesheet" href="{}/++resource++collective.markdownplus/markdownplus.css" />'.format(
                    portal_url
                ),
                '<link rel="stylesheet" href="{}/++resource++collective.markdownplus/vendor/katex/katex.min.css" />'.format(
                    portal_url
                ),
                "<style>:root { --mp-terminal-bg: %s; }</style>" % terminal_background,
                '<script src="{}/++resource++collective.markdownplus/vendor/easymde/easymde.min.js"></script>'.format(
                    portal_url
                ),
                '<script src="{}/++resource++collective.markdownplus/vendor/katex/katex.min.js"></script>'.format(
                    portal_url
                ),
                '<script src="{}/++resource++collective.markdownplus/vendor/katex/auto-render.min.js"></script>'.format(
                    portal_url
                ),
                '<script src="{}/++resource++collective.markdownplus/markdownplus.js"></script>'.format(
                    portal_url
                ),
                '<script src="{}/++resource++collective.markdownplus/vendor/mermaid/mermaid.min.js"></script>'.format(
                    portal_url
                ),
            ]
        )
