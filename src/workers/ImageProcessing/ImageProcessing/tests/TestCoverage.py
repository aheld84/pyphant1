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

u"""Provides unittest classes for CoverageWorker
"""


import unittest
import numpy


class CoverageTestCase(unittest.TestCase):
    def setUp(self):
        from pyphant.core.DataContainer import FieldContainer
        data = numpy.arange(0, 256, 1).reshape((16, 16))
        self.image = FieldContainer(data, unit=1e10)
        self.image.seal()

    def testRatiosUpToTenPercentError(self):
        delta = .1
        from ImageProcessing.CoverageWorker import CoverageWorker
        from ImageProcessing import FEATURE_COLOR, BACKGROUND_COLOR
        from pyphant.quantities import Quantity
        cworker = CoverageWorker()
        for rho1Fac in [0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0]:
            rho1 = '%s mC / m ** 3' % (3000. * rho1Fac, )
            rho2 = '3 C / m ** 3'
            cworker.paramRho1.value = rho1
            cworker.paramRho2.value = rho2
            rho1 = Quantity(rho1)
            rho2 = Quantity(rho2)
            for ratio in numpy.arange(0.0, 1.01, 0.01):
                cworker.paramW1.value = '%s%%' % (ratio * 100., )
                result = cworker.threshold(self.image)
                self.assertEqual(result.dimensions, self.image.dimensions)
                stuff1 = numpy.where(result.data == FEATURE_COLOR,
                                     True, False).sum()
                stuff2 = numpy.where(result.data == BACKGROUND_COLOR,
                                     True, False).sum()
                self.assertEqual(stuff1 + stuff2, result.data.size)
                stuff1 = (stuff1 * rho1).inUnitsOf('C / m ** 3').value
                stuff2 = (stuff2 * rho2).inUnitsOf('C / m ** 3').value
                actualRatio = stuff1 / (stuff1 + stuff2)
                self.assertTrue(abs(ratio - actualRatio) <= delta)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
