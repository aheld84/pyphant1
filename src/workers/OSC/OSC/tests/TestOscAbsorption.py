# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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

u"""Provides unittest class TestOscAbsorption.
"""

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys
import copy
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")
pkg_resources.require("pyphant.osc")

import os.path

import numpy, scipy, scipy.optimize
import pyphant.quantities as pq
import OSC.OscAbsorption as OA
from pyphant.core import DataContainer as DC

class TestOscAbsorptionCalculator(unittest.TestCase):
    "Tests the correct calculation of absorption from intensity measurements."
    def setUp(self):
        self.n = 100
        self.m = 10
        self.kappa1=0.0
        self.errLevelPos = 6
        self.errLevelCurv= 5
        self.x = numpy.linspace(-1.5,1.5,self.n)
        self.lamb = numpy.linspace(-1.0,1.0,self.m)
        X,LAMB = scipy.meshgrid(self.x,self.lamb)
        lambField = DC.FieldContainer(LAMB,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname='\lambda')
        xField = DC.FieldContainer(X[0],
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        V=[]
        for i in xrange(len(lambField.data)):
            u = xField.data
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.I = DC.FieldContainer(numpy.array(V),
                                   longname = 'intensity',
                                   shortname='I')
        self.I.dimensions[-1]=xField
        self.I0 = DC.FieldContainer(numpy.ones(self.I.data.shape,'float'),
                                   longname = 'white reference',
                                   shortname='I_0')
        self.I0.dimensions[-1]=xField
        self.Id = DC.FieldContainer(numpy.zeros(self.I.data.shape,'float'),
                                   longname = 'darf reference',
                                   shortname='I_d')
        self.Id.dimensions[-1]=xField
        self.sampleC = DC.SampleContainer([self.I,self.I0,self.Id])

    def testCalculation(self):
        """Tests the correct calculation of absorption without clipping.
        It is assumed, that the dark reference intensity is equal to zero,
        while white reference intensity is equal to one."""
        worker = OA.OscAbsorptionCalculator()
        worker.paramClipping.value = 0
        self.sampleC.seal()
        result = worker.calcAbsorption(self.sampleC)
        expectedDim = [DC.generateIndex(1,self.m),
                       DC.FieldContainer(self.x,longname='position',shortname='x',unit='1m')]
        expectedResult = DC.FieldContainer(numpy.ones((self.m,self.n),'float')-self.I.data,
                                           dimensions=expectedDim,
                                           longname=u'absorption',
                                           shortname=ur'\tilde{A}')
        self.assertEqual(result,expectedResult)

    def testCalculationWithClipping(self):
        """Tests the correct calculation of absorption with clipping.
        It is assumed, that dark reference intensity is equal to zero,
        while white reference intensity is equal to one."""
        worker = OA.OscAbsorptionCalculator()
        self.sampleC.seal()
        result = worker.calcAbsorption(self.sampleC)
        expectedDim = [DC.generateIndex(1,self.m),
                       DC.FieldContainer(self.x,longname='position',shortname='x',unit='1m')]
        afoot = numpy.ones((self.m,self.n),'float')-self.I.data
        afoot[afoot<0]=0
        afoot[afoot>1]=1
        expectedResult = DC.FieldContainer(afoot,
                                           dimensions=expectedDim,
                                           longname=u'absorption',
                                           shortname=ur'\tilde{A}')
        self.assertEqual(result,expectedResult)

    def testNegligibleNoise(self):
        """Tests the merging of abscissae data in case of negliglible deviation."""
        worker = OA.OscAbsorptionCalculator()
        worker.paramClipping.value = 0
        self.sampleC['I'].dimensions[-1].data += 1e-8*numpy.random.randn(self.n)
        self.sampleC.seal()
        result = worker.calcAbsorption(self.sampleC)
        expectedDim = [DC.generateIndex(1,self.m),
                       DC.FieldContainer(self.x,longname='position',shortname='x',unit='1m')]
        expectedResult = DC.FieldContainer(numpy.ones((self.m,self.n),'float')-self.I.data,
                                           dimensions=expectedDim,
                                           longname=u'absorption',
                                           shortname=ur'\tilde{A}')
        self.assertEqual(result,expectedResult)

    def testSignificantNoise(self):
        """Tests the conservation of abscissae data in case of significant deviation."""
        worker = OA.OscAbsorptionCalculator()
        worker.paramClipping.value = 0
        self.sampleC['I'].dimensions[-1].data += numpy.random.randn(self.n)
        self.sampleC.seal()
        result = worker.calcAbsorption(self.sampleC)
        expectedDim = copy.deepcopy(self.sampleC['I'].dimensions)
        expectedResult = DC.FieldContainer(numpy.ones((self.m,self.n),'float')-self.I.data,
                                           dimensions=expectedDim,
                                           longname=u'absorption',
                                           shortname=ur'\tilde{A}')
        self.assertEqual(result,expectedResult)

if __name__ == '__main__':
    unittest.main()
