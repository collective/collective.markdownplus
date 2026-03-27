from collective.markdownplus.renderer import render_markdown_to_html
from plone.base.utils import safe_text
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer


@implementer(ITransform)
class MarkdownToHtmlTransform:
    __name__ = "markdown_to_html"
    inputs = ("text/x-web-markdown",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **_kwargs):
        html = render_markdown_to_html(safe_text(orig))
        data.setData(safe_text(html))
        return data


def register():
    return MarkdownToHtmlTransform()
