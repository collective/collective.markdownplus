import unittest

from collective.markdownplus.testing import (
    COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING,
)
from plone.app.testing import applyProfile
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestInstallationProfile(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def test_uninstall_profile_registered(self):
        portal_setup = self.layer["portal"]["portal_setup"]
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
            [
                "markdown.extensions.fenced_code",
                "markdown.extensions.nl2br",
                "markdown.extensions.extra",
                "markdown.extensions.codehilite",
                "mdx_linkify",
            ],
            list(settings.markdown_extensions),
        )

    def test_uninstall_profile_removes_markdownplus_settings(self):
        portal = self.layer["portal"]
        applyProfile(portal, "collective.markdownplus:uninstall")
        settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix="plone")

        self.assertNotIn("text/x-web-markdown", tuple(settings.allowed_types))
        self.assertNotIn("mdx_linkify", list(settings.markdown_extensions))
