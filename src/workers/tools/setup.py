#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

__author__ = "Klaus Zimmermann, Kai Kaminski"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.1'

import setuptools

setuptools.setup(
    name = "pyphant.tools",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3'],
    packages = ['tools'],
    entry_points = """
    [pyphant.workers]
    myeentry = tools
    """,
    test_suite='tools.tests')
