from lxml import etree
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.widgets.richtext import RichTextWidget
from z3c.form.widget import FieldWidget
from zope.component.hooks import getSite

import json

try:
    from plone.app.z3cform.widgets.richtext import RichTextWidgetBase
except ImportError:
    RichTextWidgetBase = None

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
                self._set_data_attribute(
                    self,
                    "data-pat-markdownplus",
                    json.dumps(self.get_markdown_options()),
                )
            return super().render()

        textarea_widget = self._build_textarea_widget()

        mt_pattern_name = self._get_mimetype_selector_pattern_name()

        value_mime_type = (
            self.value.mimeType
            if isinstance(self.value, RichTextValue)
            else self.field.default_mime_type
        )

        if value_mime_type in MARKDOWN_MIME_TYPES:
            self._configure_markdown_textarea(textarea_widget)

        widget_map = {
            "text/html": {
                "pattern": self.pattern,
                "patternOptions": self._get_html_pattern_options(),
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

        if hasattr(textarea_widget, "update"):
            textarea_widget.update()
        return "{}\n{}".format(
            textarea_widget.render(),
            etree.tostring(mt_select, encoding="unicode"),
        )

    def _build_textarea_widget(self):
        if RichTextWidgetBase is not None:
            textarea_widget = RichTextWidgetBase(self.request)
            textarea_widget.field = self.field
            textarea_widget.name = self.name
            textarea_widget.value = self.value
            textarea_widget.id = self.id
            return textarea_widget

        base_args = getattr(self, "_base_args")()
        base_args.pop("pattern", None)
        base_args.pop("pattern_options", None)
        textarea_base = getattr(self, "_base")
        textarea_widget = textarea_base(None, None, **base_args)
        textarea_widget.klass = "form-control"
        return textarea_widget

    def _configure_markdown_textarea(self, textarea_widget):
        if RichTextWidgetBase is not None:
            textarea_widget.klass = "richTextWidget pat-markdownplus"
            self._set_data_attribute(
                textarea_widget,
                "data-pat-markdownplus",
                json.dumps(self.get_markdown_options()),
            )
            return

        textarea_widget.pattern = "markdownplus"
        textarea_widget.pattern_options = self.get_markdown_options()
        textarea_widget.klass = "form-control pat-markdownplus"

    def _get_html_pattern_options(self):
        if hasattr(self, "get_pattern_options"):
            return self.get_pattern_options()
        return getattr(self, "_base_args")().get("pattern_options", {})

    def _get_mimetype_selector_pattern_name(self):
        prefix = getattr(self, "_klass_prefix", None)
        if prefix is None:
            prefix = getattr(getattr(self, "_base"), "_klass_prefix")
        return f"{prefix}textareamimetypeselector"

    def _set_data_attribute(self, widget, attribute_name, attribute_value):
        widget.attributes[attribute_name] = attribute_value

    def get_markdown_options(self):
        preview_url = ""
        portal = getSite()
        if portal is not None:
            preview_url = f"{portal.absolute_url()}/@@markdownplus-preview"

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
