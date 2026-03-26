import unittest

from collective.markdownplus.testing import (
    COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING,
)
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestInstallationProfile(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def test_profile_allows_web_markdown_markup_type(self):
        settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix="plone")

        self.assertIn("text/x-web-markdown", settings.allowed_types)
