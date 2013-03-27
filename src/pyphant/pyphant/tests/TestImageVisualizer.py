# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""Provides unittests for ImageVisualizers. Because it is difficult
to check the correct visualization of a image, it is just checked,
wether the visualizers run without assertions."""

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys, os.path
import tempfile
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")

import numpy
from pyphant.visualizers.ImageVisualizer import ImageVisualizer
from pyphant.core import DataContainer as DC

class TestImageVisualizer(unittest.TestCase):
    """Create a two-dimensional field and check the problem-free generation of a labelled image."""
    def setUp(self):
        self.n = 100
        self.m = 10
        self.kappa1=0.0
        self.errLevelPos = 6
        self.errLevelCurv= 5
        self.tmpdir = tempfile.gettempdir()

    def testVisualization(self):
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = numpy.linspace(-1.0,1.0,self.m)
        self.xDim = numpy.linspace(-1.5,1.5,self.n)
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname='\lambda')
        xField = DC.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(lambField.data)):
            u = X[i]
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DC.FieldContainer(numpy.array(V),unit='1 V',dimensions=[lambField,xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi')

        self.V.seal()
        #Visualise result
        visualizer = ImageVisualizer(self.V,show=False)
        filename = os.path.join(self.tmpdir,'pyphant-'+DC.parseId(self.V.id)[0]+'.pdf')
        visualizer.figure.savefig(filename)

if __name__ == '__main__':
    unittest.main()
