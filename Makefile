PYGMENTIZE ?= .venv/bin/pygmentize
PYGMENTS_STYLE ?= monokai
PYGMENTS_SELECTOR ?= .codehilite
PYGMENTS_CSS ?= src/collective/markdownplus/browser/resources/pygmentize.css
PYTHON ?= .venv/bin/python
UPDATE_PREVIEW_ASSETS_SCRIPT ?= scripts/update_preview_assets.py

.PHONY: update-pygments-css update-preview-assets
update-pygments-css:
	$(PYGMENTIZE) -S $(PYGMENTS_STYLE) -f html -a $(PYGMENTS_SELECTOR) > $(PYGMENTS_CSS)

update-preview-assets:
	$(PYTHON) $(UPDATE_PREVIEW_ASSETS_SCRIPT)
