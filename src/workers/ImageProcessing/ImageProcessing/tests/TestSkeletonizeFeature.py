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

u"""Provides unittest classes TestSkeletonizeFeature, TestSkeletonizeCross, and TestCheckNeighbours.
"""


import sys
import unittest
import ImageProcessing as I
import ImageProcessing.SkeletonizeFeature as IM
import TestDistanceMapper as TDM
from pyphant.visualizers.ImageVisualizer import ImageVisualizer
import numpy
import pyphant.quantities as pq
from pyphant.core import DataContainer
import pylab

#Define helper function providing the curved feature
def ring(width=1,radius=9,center=[0,0],dim=11):
    x0, y0 = center
    circle = lambda x,y: numpy.sqrt((x-x0)**2 + (y-y0)**2)
    quarterCone = numpy.fromfunction(circle,[dim,dim])
    innerRadius = numpy.floor(float(radius)-float(width)/2)
    outerRadius = numpy.floor(float(radius)+float(width)/2)
    outer = numpy.where(quarterCone >= innerRadius,True,False)
    inner = numpy.where(quarterCone < outerRadius,True,False)
    result = numpy.where(numpy.logical_and(inner,outer),
                               I.FEATURE_COLOR,I.BACKGROUND_COLOR)
    return result

class TestSkeletonizeCurvedFeature(unittest.TestCase):
    """Tests the correct computation of skeletons from simple curved objects."""
    def setUp(self):
        #Compute thin quarter ring feature
        self.quarterRing = ring()
        #Computer broad quarter ring feature
        self.broadQuarterRing = ring(width=3)
        #get Worker
        self.worker = IM.SkeletonizeFeature(None)

    def testThinCurvedFeature(self):
        """A curved feature of one pixel width should not be altered due to the Skeletonization algorithm."""
        referenceField = DataContainer.FieldContainer(
            self.quarterRing,
            unit = '1',
            longname='Curved Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.execute(referenceField)
        numpy.testing.assert_array_equal(self.quarterRing, result.data)
        self.assertEqual(result.unit,referenceField.unit)

class TestSkeletonizeFeature(unittest.TestCase):
    """Tests the correct computation of skeletons from simple feature objects like strings."""
    def setUp(self):
        self.dim = 11
        self.worker = IM.SkeletonizeFeature(None)
        self.feature = TDM.stringFeature(self.dim,distanceToBorder=2)
        self.wideFeature=TDM.stringFeature(self.dim,width=3)

    def testSkeletonizeThinFeature(self):
        """A feature of width one is already the skeleton and should not be modified."""
        referenceField = DataContainer.FieldContainer(
            self.feature.copy(),
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.execute(referenceField)
        numpy.testing.assert_array_equal(self.feature,result.data)
        self.assertEqual(result.unit,referenceField.unit)

    def testSkeletonizeWideFeature(self):
        """The skeleton of a feature with width three is the small feature tested in the foregoing test."""
        referenceField = DataContainer.FieldContainer(
            self.wideFeature.copy(),
            unit = '1',
            longname='Simple Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.execute(referenceField)
        numpy.testing.assert_array_equal(self.feature,result.data)
        self.assertEqual(result.unit,referenceField.unit)

class TestSkeletonizeCross(TestSkeletonizeFeature):
    """Tests the correct computation of skeletons from simple feature objects like strings or crosses."""
    def setUp(self):
        self.dim = 11
        self.worker = IM.SkeletonizeFeature(None)
        self.feature = TDM.stringFeature(self.dim,directions=2,
                                         distanceToBorder=2)
        self.wideFeature=TDM.stringFeature(self.dim,width=3,directions=2)

class TestSkeletonizeBlocks(unittest.TestCase):
    """Tests the correct skeletonization of two connected blocks of features."""
    def setUp(self):
        self.dim = 11
        self.worker = IM.SkeletonizeFeature(None)
        self.skeleton = TDM.stringFeature(self.dim,distanceToBorder=2)

    def testSkeletonize(self):
        """Two 3x3 blocks of features, which are connected by a thin string of features, lead to a skeleton, which is s simple line."""
        feature = self.skeleton.copy()
        feature[1:4,4:7] = I.FEATURE_COLOR
        feature[7:10,4:7]= I.FEATURE_COLOR
        referenceField = DataContainer.FieldContainer(
            feature,
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.execute(referenceField)
        numpy.testing.assert_array_equal(self.skeleton,result.data)
        self.assertEqual(result.unit,referenceField.unit)

    def testBlockSkeletonize(self):
        """The skeleton of a simple 3x3 block is its centre pixel."""
        feature      = numpy.zeros((11,11))
        feature[:,:] = I.BACKGROUND_COLOR
        skeleton     = feature.copy()
        feature[1:4,4:7] = I.FEATURE_COLOR
        skeleton[2,5] = I.FEATURE_COLOR

        referenceField = DataContainer.FieldContainer(
            feature,
            unit = '1',
            longname='String Feature',
            shortname='S')
        referenceField.seal()
        result = self.worker.execute(referenceField)
        numpy.testing.assert_array_equal(skeleton,result.data)
        self.assertEqual(result.unit,referenceField.unit)

class TestCheckNeighbours(unittest.TestCase):
    """Tests the correct classification of neighbouring pixels."""
    def setUp(self):
        self.F = I.FEATURE_COLOR
        self.B = I.BACKGROUND_COLOR
        self.binIm = numpy.zeros((3,3))
        self.binIm[:,:] = self.B
        self.binIm[1,1] = self.F

    def assertEqualRot(self,image,proof,cases=1):
        for n in xrange(cases):
            rotIm = numpy.rot90(image,n)
            result = list(IM.checkNeighbours(rotIm)) + [IM.checkTransitions(rotIm)]
            self.assertEqual(result,proof,"The neighbourhood fingerprint should be %s, but is %s for \n%s!"%(proof,result,image))

    def testSinglePixel(self):
        """An isolated pixel has 0 feature pixels, 8 background pixels, no corner position, and 0 transitions."""
        self.assertEqualRot(self.binIm,[0,4,0,0])

    def test2CloseConnectedPixel(self):
        """If a pixel is connected to the central pixel, the latter has 1 neighboured feature pixels, 3 closely neighboured background pixels, no corner position and 1 transition from feature to background."""
        self.binIm[1,2] = self.F
        self.assertEqualRot(self.binIm,[1,3,0,1],4)

    def test2CloseConnectedBackgroundPixel(self):
        """If a background pixel is connected to the central pixel, the latter has 7 neighboured feature pixels, 1 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[1,2] = self.F
        self.assertEqualRot(self.B-self.binIm,[7,1,0,1],4)

    def test2DiagConnectedPixel(self):
        """If a pixel is connected to the central pixel at the diagonal, the latter has 1 neighboured feature pixels, 4 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.assertEqualRot(self.binIm,[1,4,0,1],4)

    def test2DiagConnectedBackgroundPixel(self):
        """If a background pixel is connected to the central pixel at the diagonal, the latter has 7 neighboured feature pixels, 0 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.assertEqualRot(self.B-self.binIm,[7,0,0,1],4)

    def test2DirectConnectedPixel(self):
        """If two pixel are directly connected to the central pixel the latter has 2 neighboured feature pixels, 3 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.binIm[0,1] = self.F
        proof = [2,3,0,1]
        self.assertEqualRot(self.binIm,proof,4)
        self.binIm[0,1] = self.B
        self.binIm[1,0] = self.F
        self.assertEqualRot(self.binIm,proof,4)

    def test2DirectConnectedBackgroundPixel(self):
        """If two background pixel are directly connected to the central pixel the latter has 6 neighboured feature pixels, 1 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.binIm[0,1] = self.F
        proof = [6,1,0,1]
        self.assertEqualRot(self.B-self.binIm,proof,4)
        self.binIm[0,1] = self.B
        self.binIm[1,0] = self.F
        self.assertEqualRot(self.B-self.binIm,proof,4)

    def test3CloseConnectedPixel(self):
        """If two pixels are connected to the central pixel, the latter has 2 neighboured feature pixels, 2 closely neighboured background pixels, no corner position, and 2 transitions from feature to background."""
        self.binIm[1,:] = self.F
        self.assertEqualRot(self.binIm,[2,2,0,2],2)

    def test3CloseConnectedBackgroundPixel(self):
        """If two background pixels are connected to the central pixel, the latter has 6 neighboured feature pixels, 2 closely neighboured background pixels, no corner position, and 2 transitions from feature to background."""
        self.binIm[1,:] = self.F
        self.assertEqualRot(self.B-self.binIm,[6,2,0,2],2)

    def test3DiagConnectedPixel(self):
        """If two pixels are connected to the central pixel on the diagonal, the latter has 2 neighboured feature pixels, 4 closely neighboured background pixels, no corner position, and 2 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.binIm[2,2] = self.F
        self.assertEqualRot(self.binIm,[2,4,0,2],2)

    def test3DiagConnectedBackgroundPixel(self):
        """If two background pixels are connected to the central pixel on the diagonal, the latter has 6 neighboured feature pixels, 0 closely neighboured background pixels, no corner position, and 2 transition from feature to background."""
        self.binIm[0,0] = self.F
        self.binIm[2,2] = self.F
        self.assertEqualRot(self.B-self.binIm,[6,0,0,2],2)

    def test3DirectConnectedPixel(self):
        """If three pixels are directly connected at an edge to the central pixel, the latter has 3 neighboured feature pixels, 3 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,:] = self.F
        self.assertEqualRot(self.binIm,[3,3,0,1],4)

    def test3DirectConnectedBackgroundPixel(self):
        """If three background pixels are directly connected at an edge to the central pixel, the latter has 6 neighboured feature pixels, 1 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,:] = self.F
        self.assertEqualRot(self.B-self.binIm,[5,1,0,1],4)

    def test3DirectConnectedPixelCorner(self):
        """If three pixels are directly connected at an corner to the central pixel, the latter has 3 neighboured feature pixels, 2 closely neighboured background pixels, and 1 transition from feature to background, while the corner position depends on the orientation of the corner."""
        self.binIm[2,:2] = self.F
        self.binIm[1,0]  = self.F
        for n in xrange(4):
            proof = [3,2,n+1,1]
            rotIm = numpy.rot90(self.binIm,n)
            result = list(IM.checkNeighbours(rotIm))+[IM.checkTransitions(rotIm)]
            self.assertEqual(result,proof,"The neighbourhood fingerprint should be %s, but is %s for \n%s!"%(proof,result,rotIm))

    def test3DirectConnectedBackgroundPixelCorner(self):
        """If three background pixels are directly connected at an corner to the central pixel, the latter has 5 neighboured feature pixels, 2 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[0,1:] = self.F
        self.binIm[1,2]  = self.F
        self.assertEqualRot(self.B-self.binIm,[5,2,0,1],4)

    def test2DirectConnectedPairsOfPixel(self):
        """If two pairs of feature or background pixels are directly connected to the central pixel the latter has 4 neighboured feature pixels, 2 closely neighboured background pixels, no corner position, and 2 transition from feature to background."""
        self.binIm[0,1:] = self.F
        self.binIm[2,1:] = self.F
        proof = [4,2,0,2]
        self.assertEqualRot(self.binIm,proof,4)
        self.assertEqualRot(self.B-self.binIm,proof,4)

    def test2DiagConnectedPairsOfPixel(self):
        """If two pairs of feature or background pixels are directly connected to the central pixel the latter has 4 neighboured feature pixels, 2 closely neighboured background pixels, no corner position, and 2 transition from feature to background."""
        self.binIm[0,0:2] = self.F
        self.binIm[2,1:] = self.F
        proof = [4,2,0,2]
        self.assertEqualRot(self.binIm,proof,4)
        self.assertEqualRot(self.B-self.binIm,proof,4)

    def test2x3Block(self):
        """If five feature pixels are connected in a single block to the  central pixel the latter has 5 neighboured feature pixels, 1 closely neighboured background pixels, no corner position, and 1 transition from feature to background."""
        self.binIm[:,1:] = self.F
        proof = [5,1,0,1]
        self.assertEqualRot(self.binIm,proof,4)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)

