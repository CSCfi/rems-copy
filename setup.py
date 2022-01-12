"""PIP Installation."""

from setuptools import setup

setup(
    name="rems-copy",
    version="0.2.1",
    description="Copies REMS licenses, resources, forms and catalogue items from one environment to another",
    author="CSC - IT Center for Science",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=[
        "rems_copy",
        "rems_copy/licenses",
        "rems_copy/forms",
        "rems_copy/workflows",
        "rems_copy/resources",
        "rems_copy/catalogue",
        "rems_copy/languages",
        "rems_copy/categories",
    ],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "rems-copy=rems_copy.main:main",
        ],
    },
)
