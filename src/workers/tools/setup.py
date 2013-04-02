#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Tools toolbox
Visit http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b2.dev'

import setuptools

setuptools.setup(
    name="pyphant.tools",
    version=VERSION,
    author="Alexander Held, Klaus Zimmermann",
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=1.0b2.dev'],
    packages=['tools'],
    entry_points="""
    [pyphant.workers]
    myeentry = tools
    """,
    test_suite='tools.tests'
    )
