#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Tools toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

__author__ = "Alexander Held, Klaus Zimmermann"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.8a2'

import setuptools

setuptools.setup(
    name="pyphant.tools",
    version=VERSION,
    author=__author__,
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=0.8a2'],
    packages=['tools'],
    entry_points="""
    [pyphant.workers]
    myeentry = tools
    """,
    test_suite='tools.tests'
    )
