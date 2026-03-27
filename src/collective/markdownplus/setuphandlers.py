from Products.CMFCore.utils import getToolByName

DEFAULT_TRANSFORM_MODULE = "Products.PortalTransforms.transforms.markdown_to_html"
MARKDOWNPLUS_TRANSFORM_MODULE = "collective.markdownplus.portaltransform"
TRANSFORM_ID = "markdown_to_html"


def _replace_transform(site, module_name):
    portal_transforms = getToolByName(site, "portal_transforms")
    existing = getattr(portal_transforms, TRANSFORM_ID, None)

    if existing is not None and getattr(existing, "module", "") == module_name:
        return

    if existing is not None:
        portal_transforms.unregisterTransform(TRANSFORM_ID)

    portal_transforms.manage_addTransform(TRANSFORM_ID, module_name)


def _get_site(context):
    return context.getSite() if hasattr(context, "getSite") else context


def install_portal_transform(context):
    site = _get_site(context)
    _replace_transform(site, MARKDOWNPLUS_TRANSFORM_MODULE)


def uninstall_portal_transform(context):
    site = _get_site(context)
    _replace_transform(site, DEFAULT_TRANSFORM_MODULE)
