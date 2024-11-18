#!/usr/bin/env python

from setuptools import setup, find_packages


with open("requirements.txt") as reqs:
    requirements = reqs.read().splitlines()

setup(
    name="keyforge",
    description="Analyze keyforge match data",
    packages=find_packages(),
    install_requires=requirements,
)
