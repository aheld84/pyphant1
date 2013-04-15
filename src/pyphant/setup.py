#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '1.0b2'

setup(
    name='pyphant',
    version=VERSION,
    description='Workflow modelling app',
    author='Alexander Held, Andreas W. Liehr, Klaus Zimmermann',
    author_email='alexander.held@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    license="BSD",
    url='http://pyphant.sourceforge.net/',
    install_requires=[
        'sogl>=0.2.0',
        'paste',
        'simplejson',
        'matplotlib',
        'numpy',
        'scipy',
        'tables',
        'wxPython',
        'egenix-mx-base',
        'configobj',
        ],
    packages=find_packages(),
    entry_points={'gui_scripts': [
        'wxPyphant = pyphant.wxgui2.wxPyphantApplication:startWxPyphant'
        ]},
    include_package_data=True,
    test_suite='pyphant.tests'
    )
