#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b3'

from setuptools import setup, find_packages
from setuptools.command.test import test


class EnsureAggUnittests(test):
    def run_tests(self):
        from pyphant.mplbackend import ensure_mpl_backend
        ensure_mpl_backend('agg')
        return test.run_tests(self)


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
        'pyphant>=1.0b3',
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
    cmdclass={'test': EnsureAggUnittests},
    test_suite='OSC.tests'
    )
