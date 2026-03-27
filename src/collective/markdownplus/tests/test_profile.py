from collective.markdownplus.interfaces import IMarkdownPlusSettings
from collective.markdownplus.renderer import DEFAULT_MARKDOWN_EXTENSIONS
from collective.markdownplus.settings import DEFAULT_PYGMENTS_STYLE
from collective.markdownplus.settings import DEFAULT_TERMINAL_BACKGROUND
from collective.markdownplus.setuphandlers import DEFAULT_TRANSFORM_MODULE
from collective.markdownplus.setuphandlers import MARKDOWNPLUS_TRANSFORM_MODULE
from collective.markdownplus.testing import COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING
from plone.app.testing import applyProfile
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class TestInstallationProfile(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def test_uninstall_profile_registered(self):
        portal = self.layer["portal"]
        assert portal is not None
        portal_setup = portal["portal_setup"]
        profile_ids = [info["id"] for info in portal_setup.listProfileInfo()]

        self.assertIn(
            "collective.markdownplus:uninstall",
            profile_ids,
        )

    def test_profile_configures_markup_settings(self):
        settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix="plone")

        self.assertEqual(
            ("text/html", "text/x-web-markdown"),
            tuple(settings.allowed_types),
        )
        self.assertEqual(
            DEFAULT_MARKDOWN_EXTENSIONS,
            list(settings.markdown_extensions),
        )

    def test_profile_installs_custom_markdown_portal_transform(self):
        portal = self.layer["portal"]
        assert portal is not None

        self.assertEqual(
            MARKDOWNPLUS_TRANSFORM_MODULE,
            portal.portal_transforms.markdown_to_html.module,
        )

    def test_profile_configures_markdownplus_settings(self):
        settings = getUtility(IRegistry).forInterface(
            IMarkdownPlusSettings,
            prefix="collective.markdownplus",
        )

        self.assertEqual(DEFAULT_PYGMENTS_STYLE, settings.pygments_style)
        self.assertEqual(DEFAULT_TERMINAL_BACKGROUND, settings.terminal_background)

    def test_uninstall_profile_removes_markdownplus_settings(self):
        portal = self.layer["portal"]
        assert portal is not None
        applyProfile(portal, "collective.markdownplus:uninstall")
        settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix="plone")

        self.assertNotIn("text/x-web-markdown", tuple(settings.allowed_types))
        self.assertNotIn("mdx_linkify", list(settings.markdown_extensions))
        self.assertNotIn("pymdownx.arithmatex", list(settings.markdown_extensions))
        self.assertNotIn("pymdownx.tilde", list(settings.markdown_extensions))
        self.assertNotIn("pymdownx.tasklist", list(settings.markdown_extensions))
        self.assertEqual(
            DEFAULT_TRANSFORM_MODULE,
            portal.portal_transforms.markdown_to_html.module,
        )
