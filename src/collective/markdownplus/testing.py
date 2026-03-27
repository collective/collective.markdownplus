from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer


class CollectiveMarkdownPlusLayer(PloneSandboxLayer):
    def setUpZope(self, app, configurationContext):
        import collective.markdownplus

        self.loadZCML(package=collective.markdownplus)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.markdownplus:default")


COLLECTIVE_MARKDOWNPLUS_FIXTURE = CollectiveMarkdownPlusLayer()

COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MARKDOWNPLUS_FIXTURE,),
    name="CollectiveMarkdownPlus:Integration",
)
