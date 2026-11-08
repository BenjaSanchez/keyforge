#!/usr/bin/env python

from setuptools import setup, find_packages


with open("requirements.txt") as reqs:
    requirements = reqs.read().splitlines()

setup(
    name="keyforge",
    description="Analyze keyforge match data",
    packages=find_packages(),
    package_data={"keyforge": ["assets/*.html", "assets/*.css"]},
    install_requires=requirements,
    entry_points={"console_scripts": ["keyforge-dashboard=keyforge.main:main"]},
)
