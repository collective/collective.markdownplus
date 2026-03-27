from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer

import collective.markdownplus

COLLECTIVE_MARKDOWNPLUS_FIXTURE = PloneWithPackageLayer(
    zcml_package=collective.markdownplus,
    zcml_filename="configure.zcml",
    gs_profile_id="collective.markdownplus:default",
    name="CollectiveMarkdownPlus:Fixture",
)

COLLECTIVE_MARKDOWNPLUS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MARKDOWNPLUS_FIXTURE,),
    name="CollectiveMarkdownPlus:Integration",
)
