from collective.markdownplus.browser.widget import MarkdownEditorFieldWidget
from collective.markdownplus.browser.widget import MarkdownEditorWidget
from collective.markdownplus.testing import COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.publisher.browser import TestRequest
from zope.schema import Text

import unittest


class TestWidgetFactory(unittest.TestCase):
    def test_field_widget_factory_sets_rows(self):
        field = Text(__name__="body", title="Body")
        request = TestRequest()

        widget = MarkdownEditorFieldWidget(field, request)

        self.assertEqual(16, widget.rows)

    def test_markdown_widget_default_options(self):
        widget = MarkdownEditorWidget(TestRequest())

        self.assertEqual(
            {"preview": True, "theme": "light", "previewUrl": ""},
            widget.get_markdown_options(),
        )


class TestRichTextMarkdownWidget(unittest.TestCase):
    layer = COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING

    def setUp(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix="plone")
        settings.allowed_types = ("text/html", "text/x-web-markdown")
        self.request = self.layer["request"]

    def test_renders_mimetype_selector_and_marks_markdown_textarea(self):
        field = RichText(
            __name__="body", title="Body", default_mime_type="text/x-web-markdown"
        )
        widget = MarkdownEditorFieldWidget(field, self.request)
        widget.context = self.layer["portal"]
        widget.value = RichTextValue(
            "## This is a test", mimeType="text/x-web-markdown"
        )

        rendered = widget.render()

        self.assertIn("pat-textareamimetypeselector", rendered)
        self.assertIn("pat-markdownplus", rendered)
        self.assertIn("data-pat-markdownplus", rendered)
