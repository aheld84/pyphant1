#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Tools toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

VERSION = '1.0b3.dev'

from setuptools import setup, find_packages

setup(
    name="pyphant.tools",
    version=VERSION,
    author="Alexander Held, Klaus Zimmermann",
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=1.0b3.dev'],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myeentry = tools
    """,
    include_package_data=True,
    test_suite='tools.tests'
    )
