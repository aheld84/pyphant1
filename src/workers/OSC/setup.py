#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""

__author__ = "Andreas W. Liehr, Klaus Zimmermann"

__revision__ = '$Revision: 25 $'

VERSION = '1.0b2.dev'

import setuptools

setuptools.setup(
    name="pyphant.osc",
    version=VERSION,
    author=__author__,
    author_email='klaus.zimmermann@fmf.uni-freiburg.de',
    maintainer='Klaus Zimmermann',
    maintainer_email='klaus.zimmermann@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=1.0b2.dev'],
    packages=['OSC'],
    entry_points="""
    [pyphant.workers]
    myeentry = OSC
    """,
    test_suite='OSC.tests'
    )
