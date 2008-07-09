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

u"""Provides unittest class TestMedianizer
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")

import ImageProcessing.Medianiser as IM
import numpy
import Scientific.Physics.PhysicalQuantities as pq
from pyphant.core import DataContainer

class TestMedianizer(unittest.TestCase):
    def setUp(self):
        self.dim = 11
        self.worker = IM.Medianiser(None)
        self.referenceField = DataContainer.FieldContainer(
            numpy.fromfunction(lambda i,j: i,[self.dim,self.dim]),
            longname='Linear Reference Field',
            shortname='R')
        self.referenceField.seal()
        self.testField = DataContainer.FieldContainer(
            self.referenceField.data.copy(),
            longname='Noisy Field with central perturbation',
            shortname='R_n')

    def testRemoveIntermediate(self):
        """Median filter with 3x3 kernel removes single perturbation with one run."""
        self.worker.paramSize.value = 3
        self.worker.paramRuns.value = 1
        self.testField.data[self.dim/2,self.dim/2] = 0
        self.testField.seal()
        result = self.worker.medianize(self.testField)
        numpy.testing.assert_array_equal(self.referenceField.data, result.data)

    def testFieldUnit(self):
        """Test replication of field unit."""
        result = self.worker.medianize(self.referenceField)
        assert(result.unit == self.referenceField.unit)

    def testDimensions(self):
        """Test correct copying of field dimensions."""
        result = self.worker.medianize(self.referenceField)
        assert(result.dimensions == self.referenceField.dimensions)

if __name__ == '__main__':
    unittest.main()
