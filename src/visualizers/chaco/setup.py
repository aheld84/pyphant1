#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

u"""
Pyphant Chaco Visualizers
This package contains visualizers that make use of the enthought.chaco
package.
"""

__author__ = "Klaus Zimmermann, Andreas W. Liehr"

__id__ = '$Id$'
__revision__ = '$Revision: 25 $'

VERSION = '0.1'

from setuptools import setup, find_packages

setup(
    name = "pyphant_chaco_visualizer",
    version = VERSION,
    author = __author__,
    description = __doc__,
    install_requires=['pyphant>=0.4alpha3',
                      'enthought.chaco2'],
    packages = find_packages(),
    entry_points = """
    [pyphant.visualizers]
    pil.image = chaco.ImageVisualizer:PlotFrame
    """
    )

