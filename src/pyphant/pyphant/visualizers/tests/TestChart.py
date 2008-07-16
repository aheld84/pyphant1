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

u"""Provides unittests for ImageVisualizers. Because it is difficult to check the correct visualization of a image, it is just checked, wether the visualizers run without assertions."""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys
import tempfile
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("Pyphant")
pkg_resources.require("Pyphant_OSC")

import numpy
from pyphant.visualizers.Chart import LineChart,ScatterPlot
from pyphant.core import DataContainer as DC
import OSC.tests.TestExtremumFinder as TEF

class TestLinePlot(unittest.TestCase):
    """Create a one-dimensional field and check the problem-free generation of a line plot."""
    def setUp(self):
        self.m = 10
        self.n = 100
        self.kappa1=0.0
        self.tmpdir = tempfile.gettempdir()
        self.visualizer = LineChart

    def testVisualization(self):
        X = numpy.linspace(-1.5,1.5,self.n)
        self.lambDim = 1.0
        xField = DC.FieldContainer(X,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        self.V = DC.FieldContainer(-self.lambDim/2* X**2 + X**4/4-X*self.kappa1,
                                   unit='1 V',dimensions=[xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi',
                                   attributes={'title':'testVisualization'})
        self.V.seal()
        visualizer = self.visualizer(self.V,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(self.V.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))

    def testErrorVisualization(self):
        X = numpy.linspace(-1.5,1.5,self.n)
        self.lambDim = 1.0
        xField = DC.FieldContainer(X,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        self.V = DC.FieldContainer(-self.lambDim/2* X**2 + X**4/4-X*self.kappa1,
                                   unit='1 V',dimensions=[xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi',
                                   attributes={'title':'testErrorVisualization'})
        self.V.error = 0.1*numpy.abs(self.V.data)
        self.V.seal()
        visualizer = self.visualizer(self.V,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(self.V.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))

    def testIntersectionXArray(self):
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = X
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname=r'\lambda')
        xField = DC.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(lambField.data)):
            u = xField.data[i]
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DC.FieldContainer(numpy.array(V),unit='1 V',dimensions=[xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi',
                                   attributes={'title':'testIntersectionXArray'})
        self.V.seal()
        visualizer = self.visualizer(self.V,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(self.V.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))


    def testIntersectionXVector(self):
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = numpy.linspace(-1.5,1.5,self.n)
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname=r'\lambda')
        xField = DC.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(lambField.data)):
            u = X[i]
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DC.FieldContainer(numpy.array(V),unit='1 V',dimensions=[xField,lambField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi',
                                   attributes={'title':'testIntersectionXVector'})
        self.V.seal()
        visualizer = self.visualizer(self.V,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(self.V.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))

    def testTableIncludingNan(self):
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = numpy.linspace(-1.5,1.5,self.n)
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname=r'\lambda')
        xField = DC.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        x0,curv,mask = TEF.fixedPoints(lambField.data,kappa1=self.kappa1)
        fixedPoints = DC.FieldContainer(numpy.array(x0).transpose(),
                                        unit = xField.unit,
                                        dimensions=[lambField,DC.generateIndex(0,3)],
                                        longname = 'position of the local extrema of electric potential',
                                        shortname = 'x_0',
                                        attributes={'title':'testTableIncludingNan'})
        fixedPoints.seal()
        visualizer = self.visualizer(fixedPoints,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(fixedPoints.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))

    def testTableIncludingNanAndErrors(self):
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = numpy.linspace(-1.5,1.5,self.n)
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname=r'\lambda')
        xField = DC.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        x0,curv,mask = TEF.fixedPoints(lambField.data,kappa1=self.kappa1)
        fixedPoints = DC.FieldContainer(numpy.array(x0).transpose(),
                                        unit = xField.unit,
                                        dimensions=[lambField,DC.generateIndex(0,3)],
                                        longname = 'position of the local extrema of electric potential',
                                        shortname = 'x_0',
                                        attributes={'title':'testTableIncludingNanAndErrors'})
        fixedPoints.error = 0.1 * fixedPoints.data
        fixedPoints.seal()
        visualizer = self.visualizer(fixedPoints,show=False)
        filename = self.tmpdir+'/pyphant-'+DC.parseId(fixedPoints.id)[0]+'%s.png' % visualizer.name
        visualizer.figure.savefig(filename.replace(' ',''))

class TestScatterPlot(TestLinePlot):
    """Create a one-dimensional field and check the problem-free generation of a scatter plot."""
    def setUp(self):
        self.m = 10
        self.n = 100
        self.kappa1=0.0
        self.tmpdir = tempfile.gettempdir()
        self.visualizer = ScatterPlot

if __name__ == '__main__':
    unittest.main()
