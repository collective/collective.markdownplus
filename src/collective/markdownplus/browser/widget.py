import json

from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.widgets.richtext import RichTextWidget
from plone.app.z3cform.widgets.richtext import RichTextWidgetBase
from z3c.form.widget import FieldWidget
from zope.component.hooks import getSite


MARKDOWN_MIME_TYPES = ("text/markdown", "text/x-web-markdown")


class MarkdownEditorWidget(RichTextWidget):
    """Rich text widget with markdownplus support for markdown mime types."""

    def render(self):
        if self.mode != "display":
            return self.render_input_mode()
        return super().render()

    def render_input_mode(self):
        allowed_mime_types = self.allowedMimeTypes()
        if not allowed_mime_types or len(allowed_mime_types) <= 1:
            if self.field.default_mime_type in MARKDOWN_MIME_TYPES:
                self.klass = "richtext-widget pat-markdownplus"
                self.attributes["data-pat-markdownplus"] = json.dumps(self.get_markdown_options())
            return super().render()

        textarea_widget = RichTextWidgetBase(self.request)
        textarea_widget.field = self.field
        textarea_widget.name = self.name
        textarea_widget.value = self.value
        textarea_widget.id = self.id

        mt_pattern_name = "{}{}".format(
            self._klass_prefix,
            "textareamimetypeselector",
        )

        value_mime_type = (
            self.value.mimeType if isinstance(self.value, RichTextValue) else self.field.default_mime_type
        )

        if value_mime_type in MARKDOWN_MIME_TYPES:
            textarea_widget.klass = "richTextWidget pat-markdownplus"
            textarea_widget.attributes["data-pat-markdownplus"] = json.dumps(self.get_markdown_options())

        widget_map = {
            "text/html": {
                "pattern": self.pattern,
                "patternOptions": self.get_pattern_options(),
            },
        }

        mt_select = etree.Element("select")
        mt_select.attrib["id"] = f"{self.id}_text_format"
        mt_select.attrib["name"] = f"{self.name}.mimeType"
        mt_select.attrib["class"] = f"form-select {mt_pattern_name}"
        mt_select.attrib[f"data-{mt_pattern_name}"] = json.dumps(
            {
                "textareaName": self.name,
                "widgets": widget_map,
            }
        )

        for mime_type in allowed_mime_types:
            option = etree.Element("option")
            option.attrib["value"] = mime_type
            if value_mime_type == mime_type:
                option.attrib["selected"] = "selected"
            option.text = mime_type
            mt_select.append(option)

        textarea_widget.update()
        return "{}\n{}".format(
            textarea_widget.render(),
            etree.tostring(mt_select, encoding="unicode"),
        )

    def get_markdown_options(self):
        preview_url = ""
        portal = getSite()
        if portal is not None:
            preview_url = "{}/@@markdownplus-preview".format(portal.absolute_url())

        return {
            "preview": True,
            "theme": "light",
            "previewUrl": preview_url,
        }



def MarkdownEditorFieldWidget(field, request):
    """Factory registered for rich text fields with markdown mime types."""

    widget = FieldWidget(field, MarkdownEditorWidget(request))
    widget.rows = 16
    return widget
