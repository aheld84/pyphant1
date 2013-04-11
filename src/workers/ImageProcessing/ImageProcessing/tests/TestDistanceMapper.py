# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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

u"""
Provides unittest class TestDistanceMapper and helper function stringFeature.
"""


import sys,unittest,logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')#,
#                    filename='/tmp/myapp.log',
#                    filemode='w')

import ImageProcessing as I
import ImageProcessing.DistanceMapper as IM
from pyphant.visualizers.ImageVisualizer import ImageVisualizer
import numpy
import pyphant.quantities as pq
from pyphant.core import DataContainer
import copy

def stringFeature(Nx,width=1,directions=1,distanceToBorder=1):
    """
    Returns an array width a string-like feature (directions=1) or a
    cross feature (directions=2).
    """
    assert directions in [1,2], "Option directions has to be 1 or 2."
    featureField = numpy.zeros((Nx,Nx))
    featureField[:,:] = I.BACKGROUND_COLOR
    for d in range(directions):
        for i in xrange(distanceToBorder,Nx-distanceToBorder):
            for j in xrange((Nx-width)/2,(Nx+width)/2):
                if d==0:
                    featureField[i,j]=I.FEATURE_COLOR
                else:
                    featureField[j,i]=I.FEATURE_COLOR
    return featureField


def makeDim(longname,shortname,dimLength,dimUnit='1mum'):
    dimension = DataContainer.FieldContainer(
        numpy.linspace(0,1,dimLength),
        unit = dimUnit,
        longname = longname, shortname=shortname)
    return dimension

class TestBroadFeaturesTouchingTheBoundary(unittest.TestCase):
    def setUp(self):
        self.dim = 11
        self.worker = IM.DistanceMapper(None)
        self.dydx = 4.0
        self.xDim = DataContainer.FieldContainer(numpy.linspace(-1,1,self.dim),
                                                 unit = '1m',
                                                 longname= 'width',
                                                 shortname='w')
        self.yDim = DataContainer.FieldContainer(
            numpy.linspace(-self.dydx,self.dydx,self.dim),
            unit = '1m',
            longname= 'height',
            shortname='h')
        self.pf = numpy.array(
            [[0, 0, 0, 1],
             [0, 0, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 0],
             [1, 1, 1, 1],
             [0, 0, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 1]],'float')

    def testDistanceMappingInvertedString(self):
        """
        Consider two features, which are divided by a vertical line.
        The respective distances increase by dx for each column counted
        from the centre line.
        """
        referenceField = DataContainer.FieldContainer(
            numpy.logical_not(stringFeature(self.dim,distanceToBorder=0)),
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dx = numpy.diff(referenceField.dimensions[0].data)[0]
        for i in xrange(referenceField.data.shape[1]):
            afoot[:,i]= dx * abs(5-i)
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingNyMuchGreaterThanNx(self):
        """
        Consider two features, which are divided by a horizonzal line.
        The respective distances increase by dy for each row counted
        from the centre line.
        """
        pos = 50
        featureField = numpy.zeros((101,11))
        featureField[:,:] = I.FEATURE_COLOR
        featureField[pos,:] = I.BACKGROUND_COLOR
        referenceField = DataContainer.FieldContainer(
            featureField,
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dy = numpy.diff(referenceField.dimensions[1].data)[0]
        for i in xrange(referenceField.data.shape[0]):
            afoot[i,:]= dy * abs(pos-i)
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingNyMuchGreaterThanNxDxDy(self):
        """
        Consider two features, which are divided by a horizonzal line.
        The respective distances increase by dy for each row counted
        from the centre line.
        """
        pos = 50
        Nx=101
        featureField = numpy.zeros((Nx,11))
        featureField[:,:] = I.FEATURE_COLOR
        featureField[pos,:] = I.BACKGROUND_COLOR
        xDim = DataContainer.FieldContainer(numpy.linspace(-1,1,Nx),
                                                 unit = '1m',
                                                 longname= 'width',
                                                 shortname='w')
        referenceField = DataContainer.FieldContainer(
            featureField,
            dimensions = [xDim, self.yDim],
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dy = numpy.diff(referenceField.dimensions[1].data)[0]
        for i in xrange(referenceField.data.shape[0]):
            afoot[i,:]= dy * abs(pos-i)
        afoot=DataContainer.FieldContainer(afoot, unit=self.xDim.unit,
                                           dimensions = map(copy.deepcopy,referenceField.dimensions))
        self.assertEqual(afoot, result)

    def testDistanceMappingInvertedStringDxDy(self):
        """
        Consider two features, which are divided by a vertical line.
        The respective distances increase by dx for each column counted
        from the centre line.
        """
        referenceField = DataContainer.FieldContainer(
            numpy.logical_not(stringFeature(self.dim,distanceToBorder=0)),
            dimensions = [self.xDim, self.yDim],
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dx = numpy.diff(referenceField.dimensions[0].data)[0]
        for i in xrange(referenceField.data.shape[1]):
            afoot[:,i]= dx * abs(5-i)
        afoot=DataContainer.FieldContainer(afoot, unit=self.xDim.unit,
                                           dimensions = map(copy.deepcopy,referenceField.dimensions))
        self.assertEqual(afoot, result)

    def testDistanceMappingInvertedStringDyDx(self):
        """
        Consider two features, which are divided by a vertical line.
        The respective distances increase by dx for each column counted
        from the centre line.
        """
        self.dydx = 0.01
        self.yDim = DataContainer.FieldContainer(
            numpy.linspace(-self.dydx,self.dydx,self.dim),
            unit = '1m',
            longname= 'height',
            shortname='h')
        referenceField = DataContainer.FieldContainer(
            numpy.logical_not(stringFeature(self.dim,distanceToBorder=0)),
            dimensions = [self.xDim, self.yDim],
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dx = numpy.diff(referenceField.dimensions[0].data)[0]
        for i in xrange(referenceField.data.shape[1]):
            afoot[:,i]= dx * abs(5-i)
        afootC=DataContainer.FieldContainer(afoot, unit=self.xDim.unit,
                                           dimensions = map(copy.deepcopy,referenceField.dimensions))
        DataContainer.assertEqual(afootC, result)

    def testDistanceMappingInvertedHorizontalString(self):
        """
        Consider two features, which are divided by a horizontal line.
        The respective distances increase by dx for each row counted
        from the centre line.
        """
        referenceField = DataContainer.FieldContainer(
            numpy.rot90(numpy.logical_not(stringFeature(self.dim,distanceToBorder=0))).copy(),
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.zeros(referenceField.data.shape,'f')
        dx = numpy.diff(referenceField.dimensions[0].data)[0]
        for i in xrange(referenceField.data.shape[1]):
            afoot[:,i]= dx * abs(5-i)
        afoot=numpy.rot90(afoot)
        numpy.testing.assert_array_equal(afoot,result.data)

    def testPitchfork(self):
        referenceField = DataContainer.FieldContainer(
            self.pf,
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        dx = referenceField.dimensions[0].data[1]-referenceField.dimensions[0].data[0]
        dy = referenceField.dimensions[1].data[1]-referenceField.dimensions[1].data[0]
        rt = numpy.sqrt(dx**2+dy**2)
        afoot = numpy.array(
            [[ 2*rt, 2*dx, dx,  0],
             [rt+dx,   rt, dy, dy],
             [ 2*dx,   dx,  0, dx],
             [   dy,   dy, dy, dy],
             [    0,    0,  0,  0],
             [   dy,   dy, dy, dy],
             [ 2*dx,   dx,  0, dx],
             [rt+dx,   rt, dy, dy],
             [ 2*rt, 2*dx, dx,  0]])
        afoot=DataContainer.FieldContainer(afoot/dx,
                                           unit=referenceField.dimensions[0].unit,
                                           rescale=True)
        self.assertEqual(afoot, result)

    def testPitchforkDxDy(self):
        xDim = DataContainer.FieldContainer(numpy.linspace(-1,1,9),
                                            unit = '1m',
                                            longname= 'width',
                                            shortname='w')
        yDim = DataContainer.FieldContainer(numpy.linspace(-self.dydx,self.dydx,4),
                                            unit = '1m',
                                            longname= 'height',
                                            shortname='h')
        referenceField = DataContainer.FieldContainer(
            self.pf,
            dimensions = [xDim, yDim],
            unit = '1',
            longname='Inverted String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        dx = referenceField.dimensions[0].data[1]-referenceField.dimensions[0].data[0]
        dy = referenceField.dimensions[1].data[1]-referenceField.dimensions[1].data[0]
        rt = numpy.sqrt(dx**2+dy**2)
        afoot = numpy.array(
            [[ 3*dx, 2*dx, dx,  0],
             [rt+dx,   rt, dy, dy],
             [ 2*dx,   dx,  0, dx],
             [   dy,   dy, dy, dy],
             [    0,    0,  0,  0],
             [   dy,   dy, dy, dy],
             [ 2*dx,   dx,  0, dx],
             [rt+dx,   rt, dy, dy],
             [ 3*dx, 2*dx, dx,  0]])
        afoot=DataContainer.FieldContainer(afoot,
                                           dimensions = map(copy.deepcopy,referenceField.dimensions),
                                           unit=self.xDim.unit,rescale=True)
        self.assertEqual(afoot, result)


class TestDistanceMapperBoundary(unittest.TestCase):
    """
    Tests the correct computation of distance maps for equally spaced
    features touching the boundaries of the array
    (self.dist=self.innerDist=0) or lying inside of the array
    (self.dist=1, self.innerDist=2).
    """
    def setUp(self):
        self.dim = 11
        self.worker = IM.DistanceMapper(None)
        self.dist = 0
        self.innerDist = 0

    def testDistanceMappingString(self):
        """
        All elements of a string-like feature have distance 1 to the
        background.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,distanceToBorder=self.dist),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0)
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingSquare(self):
        """
        All elements of a 2x2 feature have distance 1 to the
        background, if the feature is located inside of the array. If
        it is localised at a corner of the domain, the corner element
        has distance 2.
        """
        data = numpy.zeros((4,4))
        data[:,:] = I.BACKGROUND_COLOR
        data[self.dist:2+self.dist,self.dist:2+self.dist]= I.FEATURE_COLOR
        referenceField = DataContainer.FieldContainer(
            data,
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0)
        if self.dist == 0:
            afoot[0,0]=2
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingDoubleString(self):
        """
        All elements of a string-like feature of width 2 have distance
        1 to the background.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,width=2,distanceToBorder=self.dist),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0)
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingTrippleString(self):
        """
        Considering a rectangular feature with a smallest edge length
        of three all outer elements have distance one to the
        background, while the inner elements have distance two to the
        background.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,width=3,distanceToBorder=self.dist),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0)
        innerString = stringFeature(self.dim,distanceToBorder=self.innerDist)
        #Compute result afoot
        afoot = numpy.where(innerString == I.FEATURE_COLOR,2.0,afoot)
        dx = referenceField.data.shape[0]
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingCross(self):
        """
        All elements of a cross-like feature except of the central
        element have distance 1 to the background. The central element
        has distance \sqrt{2} to the background.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,directions=2,distanceToBorder=self.dist),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0).astype('d')
        afoot[self.dim/2,self.dim/2]=2.0**0.5
        numpy.testing.assert_array_equal(afoot,result.data)

    def testDistanceMappingBroadCross(self):
        """
        Considering a cross, which is composed from two rectangular
        feature each having a smallest edge length of three, all outer
        elements have distance one to the background, while the inner
        elements have distance two to the background and the elements
        of the innermost 3x3 square are the roots of
        [[[2,m,2],[m,8,m],[2,m,2]] with m = (\sqrt(2)+1)^2.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,width=3,directions=2,distanceToBorder=self.dist),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)

        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0)
        innerCross = stringFeature(self.dim,directions=2,distanceToBorder=self.innerDist)
        #Compute result afoot
        afoot = numpy.where(innerCross == I.FEATURE_COLOR,2.0,afoot).astype('d')
        left = self.dim/2-1
        right= self.dim/2+2
        middle = (2.0**0.5 + 1)**2
        core = numpy.sqrt(numpy.array([[2,middle,2],[middle,8,middle],[2,middle,2]]))
        afoot[left:right,left:right] = core
        numpy.testing.assert_array_equal(afoot,result.data)

class TestDistanceMapper(TestDistanceMapperBoundary):
    """
    Tests the correct computation of distance maps for equally spaced
    features composed from one or more strings.
    """
    def setUp(self):
        self.dim = 11
        self.worker = IM.DistanceMapper(None)
        self.dist = 1
        self.innerDist = 2

    def testDistanceMappUnit(self):
        """
        The dimension of the distance map has to be compatible with
        the dimensions of the axis. But usually it should be smaller
        by several orders of magnitude.
        """
        dimLength = 10*self.dim
        referenceField = DataContainer.FieldContainer(
            stringFeature(dimLength),
            dimensions = [makeDim('width','$w$',dimLength),
                          makeDim('height','$h$',dimLength)],
            unit = '1V',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        for dim in [0,1]:
            axisUnit   = result.dimensions[dim].unit
            self.failUnless(result.unit.unit.isCompatible(axisUnit.unit),
                            'Unit of distance map has to be compatible with unit of axis.')
        self.failUnless(result.unit.unit.name() == 'nm',
                        'Unit of distance map has to be choosen appropriately.')

    def testDistanceMappRescale(self):
        """
        The dimension of the distance map has to be a rescaled version
        of the original dimensions.
        """
        dimLength = 10*self.dim
        referenceField = DataContainer.FieldContainer(
            stringFeature(dimLength),
            dimensions = [makeDim('width','$w$',dimLength,dimUnit='1000nm'),
                          makeDim('height','$h$',dimLength,dimUnit='1000nm')],
            unit = '1V',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        for dim in [0,1]:
            axisUnit   = result.dimensions[dim].unit
            self.assertEqual(axisUnit.unit.name(),'mum',
                             'Unit of distance should me mum but is %s.' % axisUnit.unit.name())
        self.failUnless(result.unit.unit.name() == 'nm',
                        'Unit of distance map has to be choosen appropriately.')


class TestDistanceMapperDimensions(unittest.TestCase):
    """
    The distance maps are not correct if
    - the units of the dimensions differ
    - one of the dimensions is unequally spaced
    - the spacial discretisation of the dimensions differs
    In all cases an error has to be raised.
    """
    def setUp(self):
        self.dim = 11
        self.worker = IM.DistanceMapper(None)
        self.field = stringFeature(self.dim,width=3,directions=2)

    def testUnequalDimensionUnits(self):
        """
        Check for assertion if the units of the dimension
        DataContainer differ.
        """
        defaultDim = DataContainer.FieldContainer(numpy.linspace(1,11,11))
        exceptDim = DataContainer.FieldContainer(defaultDim.data.copy(),
                                                 unit='1m')

        referenceField = DataContainer.FieldContainer(self.field,
                                        unit = '1',
                                        dimensions=[defaultDim,exceptDim],
                                        longname='String Feature',
                                        shortname='S')
        referenceField.seal()
        self.assertRaises(ValueError,self.worker.calculateDistanceMap,
                          referenceField)

    def testNoContinuousDiscretisation(self):
        """
        Check for assertion if one of the dimensions is unequally
        spaced.
        """
        defaultDim = DataContainer.FieldContainer(numpy.linspace(1,11,11))

        exceptDim = DataContainer.FieldContainer(defaultDim.data.copy())
        exceptDim.data[5]=exceptDim.data[5]+0.1

        referenceField = DataContainer.FieldContainer(self.field,
                                        unit = '1',
                                        dimensions=[defaultDim,exceptDim],
                                        longname='String Feature',
                                        shortname='S')
        referenceField.seal()
        self.assertRaises(ValueError,self.worker.calculateDistanceMap,
                          referenceField)

    def testNoContinuousDiscretisationBoth(self):
        """
        Check for assertion if the dimensions are unequally spaced.
        """
        defaultDim = DataContainer.FieldContainer(numpy.linspace(1,11,11))
        defaultDim.data[5]=defaultDim.data[5]+0.1

        exceptDim = DataContainer.FieldContainer(defaultDim.data.copy())


        referenceField = DataContainer.FieldContainer(self.field,
                                        unit = '1',
                                        dimensions=[defaultDim,exceptDim],
                                        longname='String Feature',
                                        shortname='S')
        referenceField.seal()
        self.assertRaises(ValueError,self.worker.calculateDistanceMap,
                          referenceField)

    def testDifferentDimensionLength(self):
        """
        No exception should be raised if the discretisation is
        correct, but the length of the dimension vectors differ.
        """

        defaultDim = DataContainer.FieldContainer(numpy.linspace(1,11,11))
        exceptDim = DataContainer.FieldContainer(numpy.linspace(1,10,10))
        field = numpy.fromfunction(lambda i,j: i,[11,10])

        referenceField = DataContainer.FieldContainer(field,
                                        unit = '1',
                                        dimensions=[defaultDim,exceptDim],
                                        longname='String Feature',
                                        shortname='S')
        referenceField.seal()
        try:
            result = self.worker.calculateDistanceMap(referenceField)
        except ValueError,e:
            self.failIf(True,
                        "No ValueError should be raised, if the discretisation"
                        +" of two dimension vectors is correct, but the lenght"
                        +" of the vectors differ.")

class TestDifferentDiscretisation(unittest.TestCase):
    """
    Unittest TestCase checking the correct computation of distance
    maps if the discretisation of x- and y-axis differ.
    """
    def setUp(self):
        self.dim = 11
        self.worker = IM.DistanceMapper(None)
        self.dist = 0
        self.innerDist = 0
        self.dx = 1.0/(self.dim-1)
        self.dy = 2.0/(self.dim-1)
        self.dydx = self.dy/self.dx
        self.xDim = DataContainer.FieldContainer(numpy.linspace(0,1,self.dim),
                                                 unit = '1m',
                                                 longname= 'width',
                                                 shortname='w')
        self.yDim = DataContainer.FieldContainer(
            numpy.linspace(0,self.dydx,self.dim),
            unit = '1m',
            longname= 'height',
            shortname='h')

    def testDistanceMappingVerticalString(self):
        """
        All elements of a perpendicular string-like feature have
        distance dx to the background.
        """
        referenceField = DataContainer.FieldContainer(
            stringFeature(self.dim,distanceToBorder=self.dist),
            dimensions=[self.xDim,self.yDim],
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = DataContainer.FieldContainer(
            numpy.where(referenceField.data == I.FEATURE_COLOR,self.dx,0),
            dimensions=map(copy.deepcopy,[self.xDim,self.yDim]),
            unit = self.xDim.unit,
            rescale=True)
        self.assertEqual(afoot,result)

    def testDistanceMappingHorizontalString(self):
        """
        The elements of a horizontal string-like feature spanning the
        whole domain have distance dy/dx to the background.
        """
        referenceField = DataContainer.FieldContainer(
            numpy.rot90(stringFeature(self.dim,distanceToBorder=self.dist)),
            dimensions=[self.xDim,self.yDim],
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        #Compute result afoot
        afoot = DataContainer.FieldContainer(
            numpy.where(referenceField.data == I.FEATURE_COLOR,self.dy,0),
            dimensions=map(copy.deepcopy,[self.xDim,self.yDim]),
            unit = self.xDim.unit,
            rescale=True)
        self.assertEqual(afoot,result)

    def testDistanceMappingHorizontalString2(self):
        """
        The inner elements of a horizontal string-like feature, which
        does not span the whole domain have distance dy to the
        background, while the tips have distance dx to the background.
        """
        referenceField = DataContainer.FieldContainer(
            numpy.rot90(stringFeature(self.dim,distanceToBorder=self.dist+1)),
            dimensions=[self.xDim,self.yDim],
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.calculateDistanceMap(referenceField)
        #Compute result afoot
        afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,self.dy,0)
        afoot[5,1]=self.dx
        afoot[5,9]=self.dx
        afoot = DataContainer.FieldContainer(afoot,
                                             dimensions=map(copy.deepcopy,[self.xDim,self.yDim]),
                                             unit = self.xDim.unit,
                                             rescale=True)
        self.assertEqual(afoot,result)

    def testDistanceMappingCross(self):
        """
        All elements of a cross-like feature, which span across the
        whole domain, are dx and dy for the vertical and the
        horizontal bar, respectively. The central element has distance
        3dx if dy>=7**0.5, otherwise it is (dx**2+dy**2)**0.5.
        """
        smallDim = DataContainer.FieldContainer(
            numpy.linspace(0,8**0.5,self.dim),
            unit = '1m',
            longname= 'height',
            shortname='h')
        for yDim in [self.yDim,smallDim]:
            referenceField = DataContainer.FieldContainer(
                stringFeature(self.dim,directions=2,distanceToBorder=self.dist),
                dimensions=[self.xDim,yDim],
                unit = '1',
                longname='String Feature',
                shortname='S')
            referenceField.seal()
            result = self.worker.calculateDistanceMap(referenceField)
            #Compute result afoot
            afoot = numpy.where(referenceField.data == I.FEATURE_COLOR,1.0,0).astype('d')
            dx,dy = map(lambda dim: dim.data[1]-dim.data[0],[self.xDim,yDim])
            afoot[5,:] = dy/dx
            if  dy <= dx*7.0**0.5:
                centerDist = numpy.sqrt(1.0+(dy/dx)**2)
            else:
                centerDist = 3.0
            afoot[self.dim/2,self.dim/2]=centerDist
            numpy.testing.assert_array_almost_equal(afoot,result.data)

if __name__ == '__main__':
    unittest.main()
