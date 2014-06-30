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

u"""Provides unittest classes for Gradient worker
"""

import unittest
import numpy as np
from ImageProcessing.Gradient import Gradient
from pyphant.core.DataContainer import FieldContainer
from pyphant.quantities import Quantity
import copy


class GradientTestCase(unittest.TestCase):
    def testUnits(self):
        data = (np.arange(0, 256, .01)).reshape((80, 320))
        image = FieldContainer(data, unit=Quantity('1 mJ'))
        for dim in image.dimensions:
            dim.unit = Quantity('1 cm')
        image.seal()
        gradient = Gradient()
        result = gradient.gradientWorker(image)
        self.assertEqual(result.dimensions, image.dimensions)
        self.assertEqual(result.unit, Quantity('1 mJ / cm'))

    def testNonUniformAxes(self):
        im = np.array(
            [
                [0., 1., 2.],
                [30., 10., 50.],
                [8., 9., 6.]
                ]
            )
        x = FieldContainer(np.array([1., 10., 200.]), unit=Quantity('1 m'))
        y = FieldContainer(np.array([0., 2., 4.]), unit=Quantity('1 cm'))
        fc = FieldContainer(im, unit=Quantity('5 V'), dimensions=[y, x])
        fc.seal()
        grad_y, grad_x = np.gradient(fc.data)
        grad_y /= np.gradient(y.data)
        grad_x /= np.gradient(x.data)
        grad_y = FieldContainer(
            grad_y, unit=fc.unit / y.unit,
            dimensions=copy.deepcopy(fc.dimensions)
            )
        grad_x = FieldContainer(
            grad_x, unit=fc.unit / x.unit,
            dimensions=copy.deepcopy(fc.dimensions)
            )
        grad_x = grad_x.inUnitsOf(grad_y)
        expected_result = FieldContainer(
            (grad_x.data ** 2 + grad_y.data ** 2) ** 0.5,
            unit=copy.deepcopy(grad_y.unit)
            )
        result = Gradient().gradientWorker(fc)
        self.assertEqual(expected_result, result)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
