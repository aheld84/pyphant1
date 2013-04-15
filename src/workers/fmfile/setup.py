#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Full Meta File Toolbox
Visit http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b2'

from setuptools import setup, find_packages

setup(
    name="pyphant.fmf",
    version=VERSION,
    author="Alexander Held, Andreas W. Liehr, Rolf Wuerdemann, " + \
        "Klaus Zimmermann",
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=[
        'pyphant>=1.0b2',
        'wxPython',
        ],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myeentry = fmfile
    [pyphant.visualizers]
    pil.image = fmfile.FMFWriter:FMFWriter
    """,
    include_package_data=True,
    test_suite='fmfile.tests'
    )
