#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""
Pyphant Full Meta File Toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

__author__ = "Klaus Zimmermann, Andreas W. Liehr"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.1'

import setuptools

setuptools.setup(
    name = "Pyphant FMF",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3'],
    packages = ['fmfile'],
    entry_points = """
    [pyphant.workers]
    myeentry = fmfile
    """,
    test_suite='fmfile.tests')
