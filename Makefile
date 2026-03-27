# Use uv to create a virtual environment with Python 3.14. the vevn must have itself uv installed.
.DEFAULT_GOAL := help
TWINE_REPOSITORY ?= pypi

.venv/bin/uv:
	uv venv --python 3.14 --with-uv

.PHONY: release
release: .venv/bin/uv  ## Release the package to PyPI using uvx and zest-releaser
	@echo "Releasing to $(TWINE_REPOSITORY)"
	@echo 'run `make release TWINE_REPOSITORY=<name>` to override'
	TWINE_REPOSITORY=$(TWINE_REPOSITORY) .venv/bin/uvx \
		--from zest-releaser \
		--with zest-releaser'[recommended]' \
		--with zestreleaser-towncrier fullrelease

.PHONY: plone.meta
plone.meta: .venv/bin/uv  ## Configure this package with plone.meta
	.venv/bin/uvx \
		--from plone.meta \
		config-package . --no-commit

##

.PHONY: help
help:  ## Show this help message
	@gawk -vG=$$(tput setaf 2) -vR=$$(tput sgr0) ' \
	  match($$0, "^(([^#:]*[^ :]) *:)?([^#]*)##([^#].+|)$$",a) { \
	   if (a[2] != "") { printf "    make %s%-18s%s %s\n", G, a[2], R, a[4]; next }\
	    if (a[3] == "") { print a[4]; next }\
	    printf "\n%-36s %s\n","",a[4]\
	  }' $(MAKEFILE_LIST)
