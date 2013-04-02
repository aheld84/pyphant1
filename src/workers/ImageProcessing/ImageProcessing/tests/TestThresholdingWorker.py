# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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
"""



import sys
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")

import ImageProcessing as I
import ImageProcessing.ThresholdingWorker as IM
import numpy
from pyphant.core import DataContainer

class TestThresholding(unittest.TestCase):
    def setUp(self):
        self.dim = 11
        self.worker = IM.ThresholdingWorker(None)
        self.referenceField = DataContainer.FieldContainer(
            numpy.fromfunction(lambda i,j: i,[self.dim,self.dim]),
            unit = '5 V/m',
            longname='Linear Reference Field',
            shortname='R')
        self.referenceField.seal()
        self.testArray = self.referenceField.data.copy()

    def testThreshold(self):
        """Test thresholding of an intermediate graylevel."""
        self.worker.paramUnit.value = 'ignore'
        for th in xrange(self.dim + 1):
            self.worker.paramThreshold.value = th
            self.testArray[:th,:] = I.FEATURE_COLOR
            self.testArray[th:,:] = I.BACKGROUND_COLOR
            result = self.worker.threshold(self.referenceField)
            numpy.testing.assert_array_equal(self.testArray, result.data)

    def testUnitThreshold(self):
        """Test thresholding of an intermediate graylevel with units."""
        self.worker.paramUnit.value = 'V / km'
        for th in xrange(self.dim + 1):
            self.worker.paramThreshold.value = 5000 * th
            self.testArray[:th,:] = I.FEATURE_COLOR
            self.testArray[th:,:] = I.BACKGROUND_COLOR
            result = self.worker.threshold(self.referenceField)
            numpy.testing.assert_array_equal(self.testArray, result.data)

    def testFieldUnit(self):
        """Test setting of field unit to arbitrary."""
        result = self.worker.threshold(self.referenceField)
        assert(result.unit == 1)

    def testDimensions(self):
        """Test correct copying of field dimensions."""
        result = self.worker.threshold(self.referenceField)
        assert(result.dimensions == self.referenceField.dimensions)

if __name__ == '__main__':
    unittest.main()
