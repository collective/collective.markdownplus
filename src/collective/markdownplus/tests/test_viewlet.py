from collective.markdownplus.browser import viewlets

import unittest


class DummyPortal:
    def absolute_url(self):
        return "http://nohost/Plone"


class TestMarkdownAssetsViewlet(unittest.TestCase):
    def test_render_includes_katex_assets(self):
        original_get_site = viewlets.getSite
        original_get_settings = viewlets.get_markdownplus_settings

        def fake_get_site():
            return DummyPortal()

        viewlets.get_markdownplus_settings = lambda: {
            "pygments_style": "dracula",
            "terminal_background": "#111111",
        }
        viewlets.getSite = fake_get_site
        try:
            rendered = object.__new__(viewlets.MarkdownAssetsViewlet).render()
        finally:
            viewlets.getSite = original_get_site
            viewlets.get_markdownplus_settings = original_get_settings

        self.assertIn(
            "++resource++collective.markdownplus/vendor/katex/katex.min.css", rendered
        )
        self.assertIn(
            "++resource++collective.markdownplus/pygments/dracula.css", rendered
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
        self.assertIn("--mp-terminal-bg: #111111", rendered)
        self.assertNotIn("cdn.jsdelivr.net", rendered)
