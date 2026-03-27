from collective.markdownplus.interfaces import IMarkdownPlusSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm


class MarkdownPlusSettingsEditForm(RegistryEditForm):
    schema = IMarkdownPlusSettings
    schema_prefix = "collective.markdownplus"
    label = "Markdown Plus"
    description = "Configure syntax highlighting and preview code block appearance."


class MarkdownPlusSettingsControlPanel(ControlPanelFormWrapper):
    form = MarkdownPlusSettingsEditForm
