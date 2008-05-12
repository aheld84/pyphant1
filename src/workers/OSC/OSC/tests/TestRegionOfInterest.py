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

u"""Provides unittest class TestErrorEstimation.
"""

__id__ = "$Id$"
__author__ = "$Author: obi $"
__version__ = "$Revision: 4164 $"
# $Source$


import sys
import unittest
import pkg_resources

pkg_resources.require("Pyphant")
pkg_resources.require("Pyphant_OSC")

import numpy,copy
import OSC.RegionOfInterest as WM
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

class TestPrune(unittest.TestCase):
    """Tests the pruning of a simple 1D FieldContainer."""
    def setUp(self):
        abscissae = numpy.linspace(0,10,101)
        dim = DataContainer.FieldContainer(abscissae,
                                           longname='time',
                                           shortname='t',unit='1s')
        self.fieldC = DataContainer.FieldContainer(-0.5*9.81*(abscissae**2),
                                                   dimensions=[dim],
                                                   longname='position',
                                                   shortname='a',
                                                   unit='1m')
        self.fieldC.seal()

    def testPruning1D(self):
        worker = WM.RegionOfInterest()
        worker.paramStart.value='1s'
        worker.paramStop.value='9s'
        result = worker.prune(self.fieldC)
        expectedDim = DataContainer.FieldContainer(numpy.linspace(1,9,81),
                                           longname='time',
                                           shortname='t',unit='1s')
        expected = DataContainer.FieldContainer(-0.5*9.81*(expectedDim.data**2),
                                                   dimensions=[expectedDim],
                                                   longname='position',
                                                   shortname='a',
                                                   unit='1m')
        expected.seal()
        DataContainer.assertEqual(result,expected)

    def testPruning1DdifferentUnits(self):
        worker = WM.RegionOfInterest()
        worker.paramStart.value='1000ms'
        worker.paramStop.value='0.009ks'
        result = worker.prune(self.fieldC)
        expectedDim = DataContainer.FieldContainer(numpy.linspace(1,9,81),
                                           longname='time',
                                           shortname='t',unit='1s')
        expected = DataContainer.FieldContainer(-0.5*9.81*(expectedDim.data**2),
                                                   dimensions=[expectedDim],
                                                   longname='position',
                                                   shortname='a',
                                                   unit='1m')
        expected.seal()
        DataContainer.assertEqual(result,expected)

    def testPruning1DincompatibleUnits(self):
        worker = WM.RegionOfInterest()
        worker.paramStart.value='1'
        worker.paramStop.value='9'
        self.assertRaises(TypeError,worker.prune,self.fieldC)

class TestPruneUnitless(unittest.TestCase):
    """Tests the pruning of a simple 1D FieldContainer."""
    def setUp(self):
        abscissae = numpy.linspace(0,10,101)
        dim = DataContainer.FieldContainer(abscissae,
                                           longname='time',
                                           shortname='t')
        self.fieldC = DataContainer.FieldContainer(-0.5*9.81*(abscissae**2),
                                                   dimensions=[dim],
                                                   longname='position',
                                                   shortname='a',
                                                   unit='1m')
        self.fieldC.seal()

    def testPruning1D(self):
        worker = WM.RegionOfInterest()
        worker.paramStart.value='1'
        worker.paramStop.value='9'
        result = worker.prune(self.fieldC)
        expectedDim = DataContainer.FieldContainer(numpy.linspace(1,9,81),
                                           longname='time',
                                           shortname='t')
        expected = DataContainer.FieldContainer(-0.5*9.81*(expectedDim.data**2),
                                                   dimensions=[expectedDim],
                                                   longname='position',
                                                   shortname='a',
                                                   unit='1m')
        expected.seal()
        DataContainer.assertEqual(result,expected)

class TestPrune2D(unittest.TestCase):
    """Tests the pruning of a two-dimensional FieldContainers."""
    def setUp(self):
        self.n = 100
        self.m = 10
        self.kappa1=0.0
        X,LAMB = numpy.meshgrid(numpy.linspace(-1.5,1.5,self.n+1),
                                numpy.linspace(-1.0,1.0,self.m+1))
        self.lambDim = LAMB[:,0]
        self.xDim = X[0]
        self.lambField = DataContainer.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname='\lambda')
        xField = DataContainer.FieldContainer(self.xDim,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(self.lambField.data)):
            u = xField.data
            V.append(-self.lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DataContainer.FieldContainer(numpy.array(V),unit='1 V',
                                   longname = 'electric potential',
                                   shortname=r'\varphi')
        self.V.dimensions[-1] = xField
        self.worker = WM.RegionOfInterest()

    def testPruningArray(self):
        self.V.seal()
        self.worker.paramStart.value='0m'
        self.worker.paramStop.value='1.5m'
        result = self.worker.prune(self.V)
        self.X,LAMB = numpy.meshgrid(numpy.linspace(0.0 ,1.5,0.5*self.n+1),
                                numpy.linspace(-1.0,1.0,self.m+1))
        xField = DataContainer.FieldContainer(self.X[0],
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(self.lambField.data)):
            u = xField.data
            V.append(-self.lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        expectedResult = DataContainer.FieldContainer(numpy.array(V),unit='1 V',
                                   longname = 'electric potential',
                                   shortname=r'\varphi')
        expectedResult.dimensions[-1] = xField
        DataContainer.assertEqual(result,expectedResult)

    def testPruning2DVector(self):
        xField = DataContainer.FieldContainer(self.xDim,
                                              unit = '1 m',
                                              longname = 'position',
                                              shortname = 'x')
        self.V.dimensions=[self.lambField,xField]
        self.V.seal()
        self.worker.paramStart.value='0m'
        self.worker.paramStop.value='1.5m'
        result = self.worker.prune(self.V)
        xField = DataContainer.FieldContainer(numpy.linspace(0.0 ,1.5,0.5*self.n+1),
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        V = []
        for i in xrange(len(self.lambField.data)):
            u = xField.data
            V.append(-self.lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        expectedResult = DataContainer.FieldContainer(numpy.array(V),unit='1 V',
                                                      dimensions=[self.lambField,xField],
                                                      longname = 'electric potential',
                                                      shortname=r'\varphi')
        DataContainer.assertEqual(result,expectedResult)

if __name__ == '__main__':
    unittest.main()
