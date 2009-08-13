#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""Provides unittest classes for AutoFocus worker.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity
from pyphant.core.DataContainer import FieldContainer, SampleContainer
from ImageProcessing import AutoFocus as AF
import numpy


class CubeTestCase(unittest.TestCase):
    def setUp(self):
        self.cube1 = AF.Cube([slice(0, 10),
                              slice(0, 10),
                              slice(0, 10)])
        self.cube2 = AF.Cube([slice(3, 5),
                              slice(4, 6),
                              slice(-5, 7)])
    def tearDown(self):
        pass

    def testEq(self):
        cube1c = AF.Cube(self.cube1.slices)
        assert self.cube1 == cube1c
        assert not self.cube1.__eq__(self.cube2)

    def testAnd(self):
        expected = AF.Cube([slice(3, 5), slice(4, 6), slice(0, 7)])
        assert self.cube1 & self.cube2 == expected

    def testOr(self):
        expected = AF.Cube([slice(0, 10), slice(0, 10), slice(-5, 10)])
        assert self.cube1 | self.cube2 == expected

    def testVolume(self):
        assert self.cube1.getVolume() == 1000
        assert self.cube2.getVolume() == 48
        assert AF.Cube([slice(0, 0),
                       slice(0, 1000),
                       slice(0, 1000)]).getVolume() == 0

    def testSubCube(self):
        expected = AF.Cube([slice(3,5 ), slice(-5, 7)])
        assert self.cube2.getSubCube([0, 2]) == expected

    def testGetEdgeLength(self):
        assert self.cube2.getEdgeLength(0) == 2
        assert self.cube2.getEdgeLength(1) == 2
        assert self.cube2.getEdgeLength(2) == 12

    def testSub(self):
        expected = AF.Cube([slice(-3, 7),
                            slice(-4, 6),
                            slice(5, 15)])
        assert self.cube1 - self.cube2 == expected

    def testCenter(self):
        expected = (5.0, 5.0, 5.0)
        assert self.cube1.getCenter() == expected


class ZTubeTestCase(unittest.TestCase):
    def setUp(self):
        slices = [slice(0, 10), slice(0, 10)]
        mask = numpy.ones((10, 10), dtype=bool)
        fslice = AF.FocusSlice(slices, 10.0, mask)
        self.ztube = AF.ZTube(fslice, 0, 1, 0.5, 0.5)
        testslices1 = [slice(3, 12), slice(2, 9)]
        mask1 = numpy.ones((9, 7), dtype=bool)
        self.testfslice1 = AF.FocusSlice(testslices1, 12.0, mask1)
        testslices2 = [slice(7, 17), slice(8, 16)]
        mask2 = numpy.ones((10, 8), dtype=bool)
        self.testfslice2 = AF.FocusSlice(testslices2, 8.0, mask2)

    def tearDown(self):
        pass

    def testMatching(self):
        assert self.ztube.match(self.testfslice1, 1)
        assert not self.ztube.match(self.testfslice2, 1.01)
        expectedyx = AF.Cube([slice(0, 12),
                              slice(0, 10)])
        expectedz = AF.Cube([slice(-1, 2)])
        assert self.ztube.yxCube == expectedyx
        assert self.ztube.zCube == expectedz
        assert self.ztube.focusedFSlice == self.testfslice1
        assert self.ztube.focusedZ == 1


class AutoFocusTestCase(unittest.TestCase):
    def setUp(self):
        from pyphant.core.KnowledgeManager import KnowledgeManager
        km = KnowledgeManager.getInstance()
        sl1 = [slice(PhysicalQuantity('1.0mm'),
                     PhysicalQuantity('2.0mm')),
               slice(PhysicalQuantity('1.5mm'),
                     PhysicalQuantity('3.5mm'))]
        sl2 = [slice(PhysicalQuantity('0.8mm'),
                     PhysicalQuantity('1.9mm')),
               slice(PhysicalQuantity('1.7mm'),
                     PhysicalQuantity('3.4mm'))]
        mask1 = numpy.ones((10, 20), dtype=bool)
        mask2 = numpy.ones((11, 17), dtype=bool)
        fsl1 = AF.FocusSlice(sl1, PhysicalQuantity('10.0mm**-3'), mask1)
        self.fsl2 = AF.FocusSlice(sl2, PhysicalQuantity('12.0mm**-3'), mask2)
        fc1 = FieldContainer(numpy.array([fsl1]))
        fc2 = FieldContainer(numpy.array([self.fsl2]))
        fc1.seal()
        fc2.seal()
        km.registerDataContainer(fc1)
        km.registerDataContainer(fc2)
        columns = [FieldContainer(numpy.array([.5, 1.0]),
                                  unit=PhysicalQuantity('1.0mm')),
                   FieldContainer(numpy.array([fc1.id, fc2.id]),
                                  longname="emd5")]
        attributes = {u'ztol': PhysicalQuantity('0.5mm')}
        self.inputSC = SampleContainer(columns, attributes=attributes)
        self.inputSC.seal()

    def tearDown(self):
        pass

    def testAutofocus(self):
        columns = AF.autofocus(self.inputSC, 0.5, 0.75)
        inclusionSC = SampleContainer(columns,
                                      "AutoFocus")
        for fc in inclusionSC.columns:
            assert fc.data.shape == (1, )
        zfc, yfc, xfc, dfc, ffc = inclusionSC.columns
        assert zfc.data[0] * zfc.unit == PhysicalQuantity('1.0mm')
        assert (yfc.data[0] * yfc.unit,
                xfc.data[0] * xfc.unit) == self.fsl2.getCenter()
        assert ffc.data[0] * ffc.unit == PhysicalQuantity('12.0mm**-3')


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
