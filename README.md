# collective.markdownplus

Plone 6 classic UI add-on that introduces a markdown-focused rich text editor
for fields configured with the MIME type `text/markdown`.

## Features in this MVP

- Markdown-aware textarea widget for `text/markdown` fields
- Client-side live preview pane
- Basic markdown coloring in preview output for headings, bold, italic, and code
- Toolbar with Bold, Italic, Code block, and Link insertion buttons
- No impact on standard `text/html` rich text fields

## Quickstart with plonex

Requirements: `plonex` is installed on your `PATH`.

The package root itself is the plonex target. `etc/plonex.yml` and
`etc/requirements.d/` live at the repository root.

```bash
# 1. Clone / cd into this repository
cd /path/to/collective.markdownplus

# 2. Run the one-step bootstrap
./scripts/plonex-quickstart.sh

# Admin credentials default to admin/admin. Override before calling:
#   PLONEX_ADMIN_USER=myuser PLONEX_ADMIN_PASSWORD=secret ./scripts/plonex-quickstart.sh

# 3. Start the foreground development server (also the default action)
plonex zeoclient fg
# or simply
plonex

# 4. Open the site in a browser
#   http://localhost:8080/Plone
```

### What the quickstart does

1. Runs `plonex init .` from the package root. `plonex` finds `etc/plonex.yml`
   here, creates `.venv`, and installs Plone plus this package via `-e .`
   from `etc/requirements.d/`.
2. Creates an admin user via `plonex adduser`.
3. Runs `scripts/bootstrap_site.py` via `plonex run` to create the Plone site
   and apply the `collective.markdownplus:default` GenericSetup profile.

### Day-to-day plonex commands from the package root

```bash
# Foreground server (default action)
plonex zeoclient fg

# Re-install dependencies after editing setup.py
plonex dependencies

# Add an extra package to the site
plonex install some.other.package
```

## Manual installation into an existing plonex site

1. Add an editable requirement to your site's
   `etc/requirements.d/010-collective.markdownplus.txt`:

   ```text
   -e /absolute/path/to/collective.markdownplus
   ```

2. Run `plonex dependencies` to reinstall.
3. Log in to Plone and activate the add-on in Site Setup -> Add-ons.

## Usage

Configure your rich text field with `default_mime_type="text/markdown"`.
When editing that field in classic UI, the markdown widget is used.

```python
from plone.app.textfield import RichTextField
from plone.dexterity.content import Item


class MyPage(Item):
    body = RichTextField(
        title="Body",
        default_mime_type="text/markdown",
        output_mime_type="text/html",
    )
```

The widget renders a split-pane editor on the left and a live preview on the
right. Standard `text/html` fields continue to use TinyMCE as usual.