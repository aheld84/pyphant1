# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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

u"""Provides unittest classes for Watershed worker
"""

__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import numpy
import pkg_resources
pkg_resources.require("pyphant")


class WatershedTestCase(unittest.TestCase):
    def testWatershed(self):
        from ImageProcessing.Watershed import Watershed
        from pyphant.core.DataContainer import FieldContainer
        from pyphant.quantities import Quantity
        data = numpy.zeros((10, 10), dtype='uint8')
        data[2:8, 2:8] = 1
        image = FieldContainer(data)
        for dim in image.dimensions:
            dim.unit = Quantity('1 mum')
        image.seal()
        data = numpy.zeros((10, 10), dtype='uint8')
        data[3][3] = 1
        data[4][6] = 2
        markers = FieldContainer(data)
        for dim in markers.dimensions:
            dim.unit = Quantity('1 mum')
        wshed = Watershed()
        result = wshed.wsworker(image, markers)
        self.assertEqual(result.dimensions, image.dimensions)
        from scipy.ndimage import label
        self.assertEqual(label(result.data)[1], 2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
