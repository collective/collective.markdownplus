from collective.markdownplus.settings import DEFAULT_PYGMENTS_STYLE
from collective.markdownplus.settings import DEFAULT_TERMINAL_BACKGROUND
from collective.markdownplus.settings import PYGMENTS_STYLE_NAMES
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.theme.interfaces import IDefaultPloneLayer
from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary


class IMarkdownPlusLayer(IDefaultPloneLayer, IPloneFormLayer):
    """Browser layer marker for collective.markdownplus."""


PYGMENTS_STYLE_VOCABULARY = SimpleVocabulary.fromValues(PYGMENTS_STYLE_NAMES)


class IMarkdownPlusSettings(Interface):
    pygments_style = schema.Choice(
        title="Pygments style",
        description="Syntax highlighting theme used for rendered Markdown code blocks.",
        vocabulary=PYGMENTS_STYLE_VOCABULARY,
        default=DEFAULT_PYGMENTS_STYLE,
        required=True,
    )

    terminal_background = schema.TextLine(
        title="Terminal background",
        description="CSS color value used for rendered code block backgrounds.",
        default=DEFAULT_TERMINAL_BACKGROUND,
        required=False,
    )
