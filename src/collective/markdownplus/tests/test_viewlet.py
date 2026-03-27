from collective.markdownplus.browser import viewlets

import unittest


class DummyPortal:
    def absolute_url(self):
        return "http://nohost/Plone"


class TestMarkdownAssetsViewlet(unittest.TestCase):
    def test_render_includes_katex_assets(self):
        original_get_site = viewlets.getSite
        viewlets.getSite = lambda: DummyPortal()
        try:
            rendered = viewlets.MarkdownAssetsViewlet.__new__(
                viewlets.MarkdownAssetsViewlet
            ).render()
        finally:
            viewlets.getSite = original_get_site

        self.assertIn(
            "++resource++collective.markdownplus/vendor/katex/katex.min.css", rendered
        )
        self.assertIn(
            "++resource++collective.markdownplus/vendor/katex/katex.min.js", rendered
        )
        self.assertIn(
            "++resource++collective.markdownplus/vendor/katex/auto-render.min.js",
            rendered,
        )
        self.assertIn(
            "++resource++collective.markdownplus/vendor/mermaid/mermaid.min.js",
            rendered,
        )
        self.assertIn("++resource++collective.markdownplus/markdownplus.js", rendered)
        self.assertNotIn("cdn.jsdelivr.net", rendered)
