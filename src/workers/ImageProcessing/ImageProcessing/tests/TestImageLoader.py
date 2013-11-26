# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""Provides unittest class TestImageLoader.
"""



import sys
import unittest
import pkg_resources
import ImageProcessing.ImageLoaderWorker as IL
import PIL.Image as Image
import scipy, numpy
import scipy.misc
import pyphant.quantities as pq

class TestImageLoader(unittest.TestCase):
    def setUp(self):
        self.worker = IL.ImageLoaderWorker(None)
        self.demoFile = pkg_resources.resource_filename(
            'ImageProcessing', 'tests/resources/misc/demo.png'
            )
        self.worker.paramFilename.value = self.demoFile

    def testLoadGs(self):
        """Check for correct loading of greyscale image (raw data, no dimensions)."""
        orig = Image.open(self.demoFile)
        orig = scipy.misc.fromimage(orig, flatten=True)
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        numpy.testing.assert_array_equal(orig, gs.data)

    def testScalarFieldUnit(self):
        """Check for correct setting of scalar field unit."""
        unit = "250"
        self.worker.paramFieldUnit.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.unit, 250.)

    def testSimpleFieldUnit(self):
        """Check for correct setting of field unit in a basic case."""
        unit = "1 V/m"
        self.worker.paramFieldUnit.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.unit, pq.Quantity(unit))

    def testArbitraryFieldUnit(self):
        """Check for correct setting of field unit in an arbitrary case."""
        unit = "2345 V/m"
        self.worker.paramFieldUnit.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.unit, pq.Quantity(unit))

    def testScalarXScale(self):
        """Check for correct handling of scalar xScale."""
        unit = "20"
        self.worker.paramXScale.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.dimensions[-1].unit, 1.0)
        self.assertAlmostEqual(gs.dimensions[-1].data.max(), 20.)

    def testScalarYScale(self):
        """Check for correct handling of scalar yScale."""
        unit = "20"
        self.worker.paramYScale.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.dimensions[-2].unit, 1.0)
        self.assertAlmostEqual(gs.dimensions[-2].data.max(), 20.)

    def testSimpleXScale(self):
        """Check for correct handling of xScale."""
        unit = "32 m"
        punit = pq.Quantity(unit)
        self.worker.paramXScale.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.dimensions[-1].unit.unit, punit.unit)
        self.assertEqual(gs.dimensions[-1].unit.value, 1)
        self.assertAlmostEqual(gs.dimensions[-1].data.max(), punit.value)

    def testSimpleYScale(self):
        """Check for correct handling of yScale."""
        unit = "57 m"
        punit = pq.Quantity(unit)
        self.worker.paramYScale.value = unit
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.dimensions[-2].unit.unit, punit.unit)
        self.assertEqual(gs.dimensions[-2].unit.value, 1)
        self.assertAlmostEqual(gs.dimensions[-2].data.max(), punit.value)

    def testLink2X(self):
        """Check for correct inferrence of yScale from set xScale."""
        unit = "32 m"
        punit = pq.Quantity(unit)
        self.worker.paramXScale.value = unit
        self.worker.paramYScale.value = "link2X"
        gs = self.worker.plugLoadImageAsGreyScale.getResult()
        self.assertEqual(gs.dimensions[-2].unit.unit, punit.unit)
        self.assertEqual(gs.dimensions[-2].unit.value, 1)
        self.assertAlmostEqual(gs.dimensions[-1].data.max(), punit.value)
        self.assertEqual(gs.dimensions[-1].unit.unit, punit.unit)
        self.assertEqual(gs.dimensions[-1].unit.value, 1)
        ny, nx = gs.data.shape
        self.assertAlmostEqual(gs.dimensions[-2].data.max(), punit.value*ny/nx)



if __name__ == '__main__':
    unittest.main()
