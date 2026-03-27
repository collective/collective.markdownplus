from setuptools import find_namespace_packages
from setuptools import setup

setup(
    name="collective.markdownplus",
    version="0.1.0.dev0",
    description="Markdown editor widget for Plone rich text fields",
    long_description=(
        open("README.rst", encoding="utf-8").read()
        + "\n\n"
        + "Changelog\n---------\n\n"
        + "\n".join(open("CHANGES.rst", encoding="utf-8").read().splitlines()[3:])
    ),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
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
    license="GPL version 2",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.10",
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Plone",
        "Markdown",
        "Pygments",
        "mdx-linkify",
        "pymdown-extensions",
        "lxml",
        "plone.app.z3cform",
        "plone.app.textfield",
        "z3c.form",
        "zope.component",
        "zope.interface",
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
