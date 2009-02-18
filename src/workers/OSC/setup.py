#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

__author__ = "Klaus Zimmermann, Andreas W. Liehr"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.1'

import setuptools

setuptools.setup(
    name = "pyphant.osc",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3'],
    packages = ['OSC'],
    entry_points = """
    [pyphant.workers]
    myeentry = OSC
    """,
    test_suite='OSC.tests')
