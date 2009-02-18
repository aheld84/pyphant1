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
    name = "pyphant.fmf",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3',
                      'ConfigObj',
                      'egenix-mx-base'],
    packages = ['fmfile'],
    entry_points = """
    [pyphant.workers]
    myeentry = fmfile
    [pyphant.visualizers]
    pil.image = fmfile.FMFWriter:FMFWriter
    """,
    test_suite='fmfile.tests')
