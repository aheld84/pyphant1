#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant ImageProcessing toolbox
This is the ImageProcessing toolbox, that serves as an example off a
toolbox for the Pyphant framework. In order to use it you must have
the Pyphant framework installed first. Visit
http://pyphant.sourceforge.net for more information.
"""

__author__ = "Klaus Zimmermann, Andreas W. Liehr"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.1'

import setuptools

setuptools.setup(
    name = "pyphant.statistics",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3'],
    packages = ['Statistics'],
    entry_points = """
    [pyphant.workers]
    myeentry = Statistics
    """,
    test_suite = 'Statistics.tests')

