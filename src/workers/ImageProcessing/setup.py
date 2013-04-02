#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant ImageProcessing toolbox
This is the ImageProcessing toolbox, that serves as an example off a
toolbox for the Pyphant framework. In order to use it you must have
the Pyphant framework installed first. Visit
http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b2.dev'

import setuptools

setuptools.setup(
    name="pyphant.imageprocessing",
    version=VERSION,
    author="Alexander Held, Andreas W. Liehr, Klaus Zimmermann",
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=['pyphant>=1.0b2.dev'],
    packages=['ImageProcessing'],
    entry_points="""
    [pyphant.workers]
    myeentry = ImageProcessing
    """,
    test_suite='ImageProcessing.tests'
    )
