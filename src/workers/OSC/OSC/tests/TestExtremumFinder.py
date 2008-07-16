# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008, Rectorate of the University of Freiburg
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

u"""Provides unittest classes TestExtremumFinder and TestExtremumFinderDiscontinuousDiscretisation.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("Pyphant")
pkg_resources.require("Pyphant_OSC")

import os.path

import numpy, scipy, scipy.optimize
import Scientific.Physics.PhysicalQuantities as pq
import OSC.ExtremumFinder as EF
from pyphant.core import DataContainer as DC

def fixedPoints(lambdaVec,kappa1=0.0):
    """Compute fixed points x0 and slope f'(x0) of f(x)=-lambda*x+x**3-kappa1."""
    #Compute constants, which do not depend on parameter lambda
    oneIsqrt3 = numpy.complex(1.0,numpy.sqrt(3.0))
    oneIMsqrt3 = numpy.complex(1.0,-numpy.sqrt(3.0))
    lambdaC = (float(abs(kappa1))/2)**(2.0/3.0)
    umCounter = (2.0/3.0)**(1.0/3.0)
    umDenominator = 2.0**(1.0/3.0)*3.0**(2.0/3.0)
    ulrDenominator = 2.0**(2.0/3.0)*3.0**(1.0/3.0)
    #Intialise lists of results
    mask = []
    x0 = []
    slope=[]
    #Loop over parameter lambda
    for lamb in lambdaVec:
        #Define function returning the slope for a given set of fixed points
        def computeSlope(u0):
            return -lamb + 3.0*u0**2
        #Compute constant, which does depend on parameter lambda
        R = (numpy.complex(-9.0,0.0)*kappa1+numpy.sqrt(3)*
             numpy.sqrt(numpy.complex(27.0,0.0)*kappa1**2-
                        numpy.complex(4.0,0.0)*lamb**3))**(1.0/3.0)
        #Compute fixed points of function f(x)=-lambda*x+x**3-kappa1
        um = -umCounter*lamb/R-R/umDenominator
        ul = oneIsqrt3*lamb/(ulrDenominator*R)+oneIMsqrt3*R/(2.0*umDenominator)
        ur = oneIMsqrt3*lamb/(ulrDenominator*R)+oneIsqrt3*R/(2.0*umDenominator)
        u0 = numpy.array([um,ul,ur])
        #Only real valued results reflect existing fixed points
        u01Pos = numpy.where(numpy.abs(numpy.imag(u0))<=1E-9,True,False)
        u0Real = numpy.real(u0[u01Pos])
        #Distuinguish between sub- and supercritical parameter ranges
        if len(u0Real)==1: #subcritical
            x0.append([u0Real[0],numpy.NaN,numpy.NaN])
            mask.append(numpy.array(map(lambda x: not x,[True,False,False])))
            slope.append(numpy.array([computeSlope(u0Real[0]),numpy.NaN,numpy.NaN]))
        else:#supercritical
            u0Sorted = numpy.sort(u0Real)
            x0.append(u0Sorted)
            mask.append(numpy.array(map(lambda x: not x,[True,True,True])))
            slope.append(numpy.array(map(computeSlope,u0Sorted)))
    return x0,slope,mask

class TestExtremumFinder(unittest.TestCase):
    """Sets up a mirror symmetric bistable potential with a continuous distretisation and computes its local extrema and the respective curvatures."""
    def setUp(self):
        self.n = 1000
        self.u = numpy.linspace(-1.5,1.5,self.n)
        self.LAMBDA = 0.5
        self.kappa1=0.0
        self.xField = DC.FieldContainer(self.u,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        self.V = DC.FieldContainer(-self.LAMBDA/2* self.u**2 + self.u**4/4-self.u*self.kappa1,
                                   unit='1 V',dimensions=[self.xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi')

    def testRoots(self):
        """Test the correct computation of all local extrema for a bistable potential."""
        #Predict result
        x0,curv,mask = fixedPoints(numpy.array([self.LAMBDA]),kappa1=self.kappa1)
        curv[0]=numpy.NaN
        expectedResult = DC.FieldContainer(x0[0],
                                           unit = self.xField.unit,
                                           longname = 'position of the local extrema of electric potential',
                                           shortname = 'x_0')
        #Retrieve result from worker
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'both'
        result = w.locate(self.V)
        #Testing
        DC.assertEqual(result,expectedResult)

    def testMinima(self):
        """Test the correct computation of all local minima for a bistable potential."""
        #Predict result
        x0,curv,mask = fixedPoints(numpy.array([self.LAMBDA]),kappa1=self.kappa1)
        expectedResult = DC.FieldContainer(numpy.extract(curv[0]>0,x0[0]),
                                           unit = self.xField.unit,
                                           longname = 'position of the local minima of electric potential',
                                           shortname = 'x_0')
        #Retrieve result from worker
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'minima'
        result = w.locate(self.V)
        #Testing
        DC.assertEqual(result,expectedResult)

    def testMaxima(self):
        """Test the correct computation of all local maxima for a bistable potential."""
        #Predict result
        x0,curv,mask = fixedPoints(numpy.array([self.LAMBDA]),kappa1=self.kappa1)
        curv[0]=numpy.NaN
        expectedResult = DC.FieldContainer(numpy.extract(curv[0]<0,x0[0]),
                                           unit = self.xField.unit,
                                           longname = 'position of the local maxima of electric potential',
                                           shortname = 'x_0')
        #Retrieve result from worker
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'maxima'
        result = w.locate(self.V)
        #Testing
        DC.assertEqual(result,expectedResult)

class TestExtremumFinderTable(unittest.TestCase):
    """Sets up a mirror symmetric bistable potential with a continuous distretisation and computes its local extrema and the respective curvatures."""
    def setUp(self):
        self.n = 10000
        self.m = 10
        self.kappa1=0.0
        self.errLevelPos = 6
        self.errLevelCurv= 5
        self.test = DC.assertEqual

    def prepareDimensions(self):
        X,LAMB = scipy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = X

    def testRoots(self):
        """Test the correct computation of all local extrema for a bistable potential."""
        #Prepare dimensions
        self.prepareDimensions()
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname='\lambda')
        xField = DC.FieldContainer(self.xDim[0],
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(lambField.data)):
            u = xField.data
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DC.FieldContainer(numpy.array(V),unit='1 V',dimensions=[lambField,xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi')
        #Predict result
        x0,curv,mask = fixedPoints(lambField.data,kappa1=self.kappa1)
        error = 1.0/numpy.array(curv).transpose()
        error[:] =numpy.nan
        data = numpy.array(x0).transpose()
        expectedResult = DC.FieldContainer(data,
                                           unit = xField.unit,
                                           mask = numpy.isnan(data),
                                           dimensions=[DC.generateIndex(0,3),lambField],
                                           longname = 'position of the local extrema of electric potential',
                                           shortname = 'x_0')
        #Configure worker
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'both'
        #Retrieve result from worker
        result = w.locate(self.V)
        self.test(result,expectedResult)

class TestExtremumFinderTableFail(TestExtremumFinderTable):
    """Sets up a mirror symmetric bistable potential with a continuous distretisation, computes its local extrema and the respective curvatures. This test succeeds, if the deviation between expected and computed result due to the insufficient spatial resolution is detected."""
    def setUp(self):
        self.n = 1000
        self.m = 10
        self.kappa1=0.0
        self.errLevelPos = 6
        self.errLevelCurv= 5
        self.test = self.assertNotEqual

class TestError(unittest.TestCase):
    def testParabelExactMinimum(self):
        x = numpy.array([-2,-1,0,1,2],'float')
        y = x**2
        inputField = DC.FieldContainer(y,
                                       error=numpy.repeat(0.1,len(y)),
                                       dimensions=[DC.FieldContainer(x,longname='abscissae',shortname='x')],
                                       longname='parabel',
                                       shortname='f'
                                       )
        expectedResult = DC.FieldContainer(numpy.array([0.0]),
                                           longname = 'position of the local minimum of parabel',
                                           shortname = 'x_0',
                                           error = numpy.array([0.05])
                                           )
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'minima'
        #Retrieve result from worker
        result = w.locate(inputField)
        DC.assertEqual(result,expectedResult)

    def testParabelSymmetricallyBoxedMinimum(self):
        x = numpy.array([-2,-1,0,1,2],'float')-0.5
        y = x**2
        inputField = DC.FieldContainer(y,
                                       error=numpy.repeat(0.1,len(y)),
                                       dimensions=[DC.FieldContainer(x,longname='abscissae',shortname='x')],
                                       longname='parabel',
                                       shortname='f'
                                       )
        expectedResult = DC.FieldContainer(numpy.array([0.0]),
                                           longname = 'position of the local minimum of parabel',
                                           shortname = 'x_0',
                                           error = numpy.array([0.1])
                                           )
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'minima'
        #Retrieve result from worker
        result = w.locate(inputField)
        DC.assertEqual(result,expectedResult)

    def testParabel(self):
        x = numpy.array([-2,-1,0,1,2],'float')+0.1
        y = x**2
        inputField = DC.FieldContainer(y,
                                       error=numpy.repeat(0.1,len(y)),
                                       dimensions=[DC.FieldContainer(x,longname='abscissae',shortname='x')],
                                       longname='parabel',
                                       shortname='f')
        error  = inputField.error[slice(0,1)] / (y[1]-2*y[2]+y[3])**2
        error *= numpy.abs(y[2]-y[3]) + numpy.abs(y[1]-y[3]) + numpy.abs(y[1]-y[2])
        expectedResult = DC.FieldContainer(numpy.array([0.0]),
                                           longname = 'position of the local minimum of parabel',
                                           shortname = 'x_0',
                                           error = error)
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'minima'
        #Retrieve result from worker
        result = w.locate(inputField)
        DC.assertEqual(result,expectedResult)

    def testParabelArray(self):
        x = numpy.array([-2,-1,0,1,2],'float')
        field = numpy.array([(x-0.2)**2-0.5,(x+0.1)**2])
        inputField = DC.FieldContainer(field,
                                       error=numpy.resize(numpy.repeat(0.1,len(field)),field.shape),
                                       dimensions=[DC.FieldContainer(numpy.array([1,2]),
                                                                     longname='type',shortname=r'\theta'),
                                                   DC.FieldContainer(x,longname='position',shortname='x')],
                                       longname='parabel',
                                       shortname='f')
        def error(y):
            error  = inputField.error[0,0] / (y[1]-2*y[2]+y[3])**2
            error *= numpy.abs(y[2]-y[3]) + numpy.abs(y[1]-y[3]) + numpy.abs(y[1]-y[2])
            return error
        expectedResult = DC.FieldContainer(numpy.array([[0.2,-0.1]]),
                                           longname = 'position of the local minima of parabel',
                                           shortname = 'x_0',
                                           error = numpy.array([[error(field[0]),error(field[1])]]))
        expectedResult.dimensions[-1] = DC.FieldContainer(numpy.array([1,2]),
                                                          longname='type',
                                                          shortname=r'\theta')
        w = EF.ExtremumFinder(None)
        w.paramExtremum.value=u'minima'
        #Retrieve result from worker
        result = w.locate(inputField)
        DC.assertEqual(result,expectedResult)

class TestEstimateExtremumPosition(unittest.TestCase):
    def setUp(self):
        self.x = numpy.array([2,3,4],'f')
        self.y = numpy.array([2,1,1.5],'f')
        self.zeros = numpy.zeros((3,),'f')
        self.error = numpy.array([0.01,0.01,0.01],'f')
        
    def testExactMinimum(self):
        y = numpy.array([2,1,2],'f')
        result =  EF.estimateExtremumPosition(y,self.x)
        self.assertEqual(result,(3.0,numpy.NaN,1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(3.0,0.0,1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.error)
        numpy.testing.assert_almost_equal(numpy.array(result),
                                          numpy.array((3.0,0.005,1.0)))
        
    def testExactMaximum(self):
        y = numpy.array([2,3,2],'f')
        result =  EF.estimateExtremumPosition(y,self.x)
        self.assertEqual(result,(3.0,numpy.NaN,-1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(3.0,0.0,-1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.error)
        numpy.testing.assert_almost_equal(numpy.array(result),
                                          numpy.array((3.0,0.005,-1.0)))

    def testSymmetricMinimum(self):
        y = numpy.array([2,2,3],'f')
        result =  EF.estimateExtremumPosition(y,self.x)
        self.assertEqual(result,(2.5,numpy.NaN,1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(2.5,0.0,1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.error)
        numpy.testing.assert_almost_equal(numpy.array(result),
                                          numpy.array((2.5,0.02,1.0)))

    def testSymmetricMaximum(self):
        y = numpy.array([2,2,1],'f')
        result =  EF.estimateExtremumPosition(y,self.x)
        self.assertEqual(result,(2.5,numpy.NaN,-1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(2.5,0.0,-1.0))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.error)
        numpy.testing.assert_almost_equal(numpy.array(result),
                                          numpy.array((2.5,0.02,-1.0)))

    def testExactGeneric(self):
        result =  EF.estimateExtremumPosition(self.y,self.x)
        self.assertEqual(result,(2.5+1/1.5,numpy.NaN,1.0))
        result =  EF.estimateExtremumPosition(self.y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(2.5+1/1.5,0.0,1.0))
        result =  EF.estimateExtremumPosition(self.y,self.x,sigmaY=self.error)
        numpy.testing.assert_almost_equal(numpy.array(result),
                                          numpy.array((2.5+1/1.5,0.02/1.5**2,1.0)))

    def testConstantRegion(self):
        """A constant region does not have any local extrema and NaN values should be returned."""
        y = numpy.array([2,2,2],'f')
        result =  EF.estimateExtremumPosition(y,self.x)
        self.assertEqual(result,(numpy.NaN,numpy.NaN,numpy.NaN))
        result =  EF.estimateExtremumPosition(y,self.x,sigmaY=self.zeros)
        self.assertEqual(result,(numpy.NaN,numpy.NaN,numpy.NaN))

    def testEqualBinCentres(self):
        """Erroneous sampling points leading to identical bin centres have to intercepted."""
        x = numpy.array([2,3,2],'f')
        self.assertRaises(ValueError,EF.estimateExtremumPosition,self.y,x)

    def testFiniteBinWidth(self):
        """Erroneous sampling points leading to zero bin width have to intercepted."""
        x = numpy.array([2,2,2],'f')
        self.assertRaises(ValueError,EF.estimateExtremumPosition,self.y,x)
        x = numpy.array([2,2,3],'f')
        self.assertRaises(ValueError,EF.estimateExtremumPosition,self.y,x)
        x = numpy.array([2,3,3],'f')
        self.assertRaises(ValueError,EF.estimateExtremumPosition,self.y,x)
        
if __name__ == '__main__':
    unittest.main()
