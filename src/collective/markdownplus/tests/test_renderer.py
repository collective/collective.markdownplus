from collective.markdownplus.renderer import render_markdown_to_html
from collective.markdownplus.testing import COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

import json
import unittest


class TestRenderer(unittest.TestCase):
    def test_render_markdown_supports_gfm_and_math(self):
        source = "| a | b |\n|---|---|\n| 1 | 2 |\n\nInline math: $E=mc^2$"

        html = render_markdown_to_html(source)

        self.assertIn("<table", html)
        self.assertIn("arithmatex", html)

    def test_render_markdown_supports_extended_extensions(self):
        source = (
            "!!! note\n"
            "    Extended syntax\n\n"
            "- [x] done\n\n"
            "==highlight== and ^^inserted^^ text[^1]\n\n"
            "[^1]: footnote"
        )

        html = render_markdown_to_html(source)

        self.assertIn("admonition", html)
        self.assertIn("task-list-item", html)
        self.assertIn("<mark>", html)
        self.assertIn("<ins>", html)
        self.assertIn("footnote", html)

    def test_render_markdown_supports_strikethrough(self):
        html = render_markdown_to_html("Before ~~removed~~ after")

        self.assertIn("<del>", html)
        self.assertIn("removed", html)

    def test_render_markdown_preserves_mermaid_blocks(self):
        source = "```mermaid\ngraph TD\nA-->B\n```"

        html = render_markdown_to_html(source)

        self.assertIn('class="mp-mermaid mermaid"', html)
        self.assertIn("graph", html)
        self.assertNotIn("<svg", html)

    def test_render_markdown_uses_codehilite_wrapper_class(self):
        source = "```python\nprint('ok')\n```"

        html = render_markdown_to_html(source)

        self.assertIn('class="codehilite"', html)


class TestPreviewView(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def test_preview_view_returns_rendered_html_payload(self):
        portal = self.layer["portal"]
        request = self.layer["request"]
        request.form["text"] = "## Title\n\n$E=mc^2$"

        view = portal.restrictedTraverse("@@markdownplus-preview")
        payload = json.loads(view())

        self.assertIn("html", payload)
        self.assertIn("<h2", payload["html"])
        self.assertIn("arithmatex", payload["html"])

    def test_preview_view_preserves_mermaid_blocks(self):
        portal = self.layer["portal"]
        request = self.layer["request"]
        request.form["text"] = "```mermaid\ngraph TD\nA-->B\n```"

        view = portal.restrictedTraverse("@@markdownplus-preview")
        payload = json.loads(view())

        self.assertIn('class="mp-mermaid mermaid"', payload["html"])


class TestPortalTransforms(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def _transform_html(self, source):
        portal = self.layer["portal"]
        result = portal.portal_transforms.convertTo(
            "text/html",
            source,
            mimetype="text/x-web-markdown",
        )
        html = result.getData()
        if isinstance(html, bytes):
            html = html.decode("utf-8")
        return html

    def test_portal_transform_markdown_to_html_supports_gfm_mermaid_and_math(self):
        cases = [
            (
                "gfm table and task list",
                "| Name | Value |\n| --- | --- |\n| One | 1 |\n\n- [x] done\n- [ ] todo",
                ["<table", "task-list-item", "checkbox"],
            ),
            (
                "strikethrough and footnote",
                "Before ~~removed~~ after[^1]\n\n[^1]: Footnote text",
                ["<del>", "footnote", "removed"],
            ),
            (
                "mermaid fence",
                "```mermaid\ngraph TD\nA-->B\n```",
                ['class="mp-mermaid mermaid"', "graph TD"],
            ),
            (
                "inline and display math",
                "Inline math: $E=mc^2$\n\n$$x^2 + y^2 = z^2$$",
                ["arithmatex", "\\(E=mc^2\\)", "\\[x^2 + y^2 = z^2\\]"],
            ),
        ]

        for title, source, expected_fragments in cases:
            with self.subTest(title=title):
                html = self._transform_html(source)
                for fragment in expected_fragments:
                    self.assertIn(fragment, html)
