import importlib


ViewletBase = importlib.import_module("plone.app.layout.viewlets.common").ViewletBase
getSite = importlib.import_module("zope.component.hooks").getSite


class MarkdownAssetsViewlet(ViewletBase):
    """Inject markdownplus CSS and JS for classic UI forms."""

    index = None

    def render(self):
        portal = getSite()
        portal_url = portal.absolute_url()
        return "".join(
            [
                '<link rel="stylesheet" href="{}/++resource++collective.markdownplus/markdownplus.css" />'.format(
                    portal_url
                ),
                '<script src="{}/++resource++collective.markdownplus/markdownplus.js"></script>'.format(
                    portal_url
                ),
            ]
        )
