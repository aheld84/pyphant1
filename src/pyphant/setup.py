#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

__id__ = '$Id: $'
__revision__ = '$Revision: 25 $'

VERSION = '0.5'


from setuptools import setup, find_packages

setup( name='Pyphant',
       version = VERSION,
       description='Workflow modelling app',
       author='Klaus Zimmermann, Andreas W. Liehr',
       author_email='klaus.zimmermann@fmf.uni-freiburg.de',
       maintainer='Klaus Zimmermann',
       maintainer_email='zklaus@sourceforge.net',
       license = "BSD",
       url='http://pyphant.sourceforge.net/',
       install_requires=['sogl>=0.2.0'
## The following are required, but currently not setuptools enabled.
#                         ,'ScientificPython>=2.6',
#                         ,'matplotlib>=0.90.1',
#                         ,'scipy>=0.5.2',
#                         ,'tables>=1.4',
#                         ,'wxPython>=2.6.3.2'
                         ],
       packages = find_packages(),
       entry_points={'gui_scripts':['wxPyphant = pyphant.wxgui2.wxPyphantApplication:startWxPyphant']},
       include_package_data = True,
       test_suite = 'pyphant.tests'
       )
