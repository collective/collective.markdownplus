"""Create a Plone site and install collective.markdownplus profile.

Intended to run with:
    plonex run scripts/bootstrap_site.py
"""

from Testing.makerequest import makerequest

import transaction

SITE_ID = "Plone"
PROFILE_ID = "profile-collective.markdownplus:default"


def _portal_exists(app, site_id):
    return site_id in app.objectIds()


def _create_portal(app, site_id):
    app.manage_addProduct["CMFPlone"].addPloneSite(
        site_id,
        extension_ids=[PROFILE_ID],
    )


def _apply_profile(portal):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile(PROFILE_ID)


def main(app):
    app = makerequest(app)

    if not _portal_exists(app, SITE_ID):
        _create_portal(app, SITE_ID)

    portal = app[SITE_ID]
    _apply_profile(portal)
    transaction.commit()

    print("Bootstrap complete")
    print(f"Site: /{SITE_ID}")
    print(f"Profile: {PROFILE_ID}")


if __name__ == "__main__":
    main(app)  # noqa: F821 - provided by Zope runner environment
