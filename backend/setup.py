#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for anyblok-background-tasks"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
import os

from setuptools import find_packages, setup

version: str = "0.1.0"
here: str = os.path.abspath(os.path.dirname(__file__))

with open(
    os.path.join(here, "README.md"), "r", encoding="utf-8"
) as readme_file:
    readme = readme_file.read()

requirements: "List[str]" = [
    "sqlalchemy",
    "anyblok",
    "anyblok_mixins",
]

test_requirements: "List[str]" = [
    # TODO: put package test requirements here
]

setup(
    name="home_thermostat",
    version=version,
    description="Home thermostat",
    long_description=readme,
    author="Pierre Verkest",
    author_email="pierreverkest84@gmail.com",
    url="https://github.com/petrus-v/anyblok-background-tasks",
    packages=find_packages(),
    entry_points={
        "bloks": ["home_thermostat=home_thermostat.home_thermostat:HomeThermostat"]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="anyblok,thermostat,iot",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
