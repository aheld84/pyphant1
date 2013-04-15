#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b3.dev'

from setuptools import setup, find_packages

setup(
    name="pyphant.osc",
    version=VERSION,
    author="Andreas W. Liehr, Klaus Zimmermann",
    author_email='klaus.zimmermann@fmf.uni-freiburg.de',
    maintainer='Klaus Zimmermann',
    maintainer_email='klaus.zimmermann@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=[
        'pyphant>=1.0b3.dev',
        'numpy',
        'scipy',
        'matplotlib',
        ],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myeentry = OSC
    """,
    include_package_data=True,
    test_suite='OSC.tests'
    )
