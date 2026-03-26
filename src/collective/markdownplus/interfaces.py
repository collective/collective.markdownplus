from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.theme.interfaces import IDefaultPloneLayer


class IMarkdownPlusLayer(IDefaultPloneLayer, IPloneFormLayer):
    """Browser layer marker for collective.markdownplus."""
