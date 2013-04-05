#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Statistics toolbox
This is the Statistics toolbox, that provides workers
for the Pyphant framework. In order to use it you must have
the Pyphant framework installed first. Visit
http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b2.dev'

from setuptools import setup, find_packages

setup(
    name="pyphant.statistics",
    version=VERSION,
    author="Alexander Held, Andreas W. Liehr, Klaus Zimmermann",
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=1.0b2.dev'],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myeentry = Statistics
    """,
    test_suite='Statistics.tests'
    )
