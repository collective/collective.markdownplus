from collective.ftw.upgrade import UpgradeStep
from plone import api
from logging import getLogger


logger = getLogger(__name__)

class RemoveTheMarkdownExtensionsMetaPlugin(UpgradeStep):
    """Remove the markdown.extensions.meta plugin.
    """

    def __call__(self):
        extensions = api.portal.get_registry_record(
            "plone.markdown_extensions", default=[]
        )
        if not "markdown.extensions.meta" in extensions:
            return


        extensions.remove("markdown.extensions.meta")
        api.portal.set_registry_record("plone.markdown_extensions", extensions)
        logger.info("Removed 'markdown.extensions.meta' from markdown extensions.")
