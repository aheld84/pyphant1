#!/usr/bin/env python
# -*- coding: utf-8 -*-

__id__ = '$Id: $'
__revision__ = '$Revision: 25 $'

VERSION = '1.0b1'


from setuptools import setup, find_packages

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
        ## The following are required,
        ## but currently not setuptools enabled.
        #'ScientificPython',
        #'matplotlib',
        #'scipy',
        #'tables',
        #'wxPython',
        #'egenix-mx-base',
        ],
    packages=find_packages(),
    entry_points={'gui_scripts':[
        'wxPyphant = pyphant.wxgui2.wxPyphantApplication:startWxPyphant'
        ]},
    include_package_data=True,
    test_suite='pyphant.tests'
    )
