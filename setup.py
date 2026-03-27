from pathlib import Path
from setuptools import setup

setup(
    name="collective.markdownplus",
    version="0.1.0.dev0",
    description="Markdown editor widget for Plone rich text fields",
    long_description="\n\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("CHANGES.md").read_text(encoding="utf-8"),
        ]
    ),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="Plone markdown richtext mockup",
    author="collective",
    author_email="collective@plone.org",
    url="https://github.com/collective/collective.markdownplus",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.markdownplus",
        "Source": "https://github.com/collective/collective.markdownplus",
        "Issue Tracker": "https://github.com/collective/collective.markdownplus/issues",
        "Changelog": "https://github.com/collective/collective.markdownplus/CHANGES.md",
    },
    license="MIT",
    license_files=("LICENSE.txt",),
    include_package_data=True,
    python_requires=">=3.10",
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Plone>=6.1",
        "Markdown",
        "Pygments",
        "mdx-linkify",
        "pymdown-extensions",
        "lxml",
        "plone.app.registry",
        "plone.app.z3cform",
        "plone.app.textfield",
        "z3c.form",
        "zope.component",
        "zope.interface",
        "zope.schema",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "pytest-plone",
            "zope.publisher",
            "zope.schema",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
