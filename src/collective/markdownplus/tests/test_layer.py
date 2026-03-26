import unittest

from collective.markdownplus.interfaces import IMarkdownPlusLayer
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.theme.interfaces import IDefaultPloneLayer


class TestBrowserLayer(unittest.TestCase):
    def test_package_layer_extends_default_plone_layer(self):
        self.assertIn(IDefaultPloneLayer, IMarkdownPlusLayer.__bases__)

    def test_package_layer_extends_plone_form_layer(self):
        self.assertIn(IPloneFormLayer, IMarkdownPlusLayer.__bases__)
