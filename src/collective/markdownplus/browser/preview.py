import json

from collective.markdownplus.renderer import render_markdown_to_html
from Products.Five import BrowserView


class MarkdownPreviewView(BrowserView):
    """Return rendered HTML for markdown preview requests."""

    def __call__(self):
        text = self.request.form.get("text", "")
        html = render_markdown_to_html(text)

        self.request.response.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps({"html": html})
