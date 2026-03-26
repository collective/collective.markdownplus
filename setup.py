from setuptools import find_namespace_packages
from setuptools import setup


setup(
    name="collective.markdownplus",
    version="0.1.0.dev0",
    description="Markdown editor widget for Plone rich text fields",
    long_description=(
        open("README.rst", encoding="utf-8").read()
        + "\n\n"
        + open("CHANGES.rst", encoding="utf-8").read()
    ),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords="Plone markdown richtext mockup",
    author="collective",
    license="GPL version 2",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Plone",
        "plone.app.z3cform",
        "plone.app.textfield",
        "z3c.form",
        "zope.interface",
        "zope.schema",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.testing",
            "pytest",
            "pytest-plone",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
