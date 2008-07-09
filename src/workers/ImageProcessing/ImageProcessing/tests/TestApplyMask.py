# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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

u"""Provides unittest classes TestApplyMask and TestApplyMask3D.
"""

__id__ = "$Id:$"
__author__ = "$Author:$"
__version__ = "$Revision:$"
# $Source$

import sys
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")

import ImageProcessing as I
import ImageProcessing.ApplyMask as IM
import TestDistanceMapper as TDM
from pyphant.visualizers.ImageVisualizer import ImageVisualizer
import numpy
import Scientific.Physics.PhysicalQuantities as pq
from pyphant.core import DataContainer
import pylab

class TestApplyMask(unittest.TestCase):
    """Tests the correct application of binary masks."""
    def setUp(self):
        self.dim = 11
        self.worker = IM.ApplyMask(None)
        self.inputField = DataContainer.FieldContainer(
            numpy.fromfunction(lambda i,j: i,[self.dim,self.dim])+100,
            unit = '1 V/m',
            longname='Linear Reference Field',
            shortname='R')
        self.inputField.seal()

        self.mask = DataContainer.FieldContainer(
            TDM.stringFeature(self.dim),
            unit = '1',
            longname='String Feature',
            shortname='S')
        self.mask.data[self.dim-1,self.dim-1] = I.FEATURE_COLOR
        self.mask.seal()

    def testReturnedField(self):
        """Checking the masked field by applying a string-like mask to the input field."""
        result = self.worker.createMaskedImage(self.inputField,self.mask)
        afoot = numpy.zeros((self.dim,self.dim)).astype('d')
        afoot[self.dim-1,self.dim-1] = 100+self.dim-1
        for i in xrange(1,self.dim-1):
            afoot[i,self.dim/2] = 100+i
        numpy.testing.assert_array_equal(afoot, result.data)
        assert(result.unit == self.inputField.unit)
        for resultDim,inputDim in zip(self.inputField.dimensions,
                                      result.dimensions):
            numpy.testing.assert_array_equal(resultDim.data,inputDim.data)
            assert(resultDim.unit == inputDim.unit,
                   'Units of input and output dimensions has to be equal.')

    def testReturnedTable(self):
        """Checking the extracted samples by applying a string-like mask to the input field."""
        result = self.worker.findMaskPoints(self.inputField,self.mask)
        xPos = range(1,self.dim)
        yPos = [self.dim/2 for i in xrange(1,self.dim-1)]
        yPos.append(self.dim-1)
        zVal = range(101,101+self.dim)
        afoot = zip(xPos,yPos,zVal)
        table = zip(result[0].data.tolist(),
                    result[1].data.tolist(),
                    result[2].data.tolist())
        for row in table:
            try:
                afoot.remove(row)
            except ValueError,e:
                self.fail('Row %s not found.' % row)

    def testReturnedTableUnits(self):
        """Checking the units of table columns."""
        result = self.worker.findMaskPoints(self.inputField,self.mask)
        checkUnits = [self.inputField.dimensions[0].unit,
                      self.inputField.dimensions[1].unit,
                      self.inputField.unit]
        for col in [0,1]:
            self.assertEqual(result[col].unit,
                             self.inputField.dimensions[col].unit,
                         "Unit of column %i has to match unit of field dimension %i." % (col,col))
        self.assertEqual(result[2].unit,self.inputField.unit,
                         "Unit of third column has to match unit of field.")
    def testValueError(self):
        """Checking the correct assertion of ValueError if the dimensions of both fields are not identical."""
        mask = DataContainer.FieldContainer(
            TDM.stringFeature(self.dim+1),
            unit = '1',
            longname='String Feature',
            shortname='S')
        mask.seal()
        for plug in [self.worker.createMaskedImage,self.worker.findMaskPoints]:
            self.assertRaises(ValueError,plug,self.inputField,mask)

class TestApplyMask3D(unittest.TestCase):
    """Tests the correct application of binary masks on three-dimensional fields."""
    def setUp(self):
        self.dim = 5
        self.worker = IM.ApplyMask(None)
        self.inputField = DataContainer.FieldContainer(
            numpy.fromfunction(lambda i,j,k: numpy.sin(i+j+k),
                               [self.dim,self.dim,self.dim]),
            unit = '1 V/m',
            longname='Linear Reference Field',
            shortname='R')
        self.inputField.seal()

        featureField = numpy.zeros((self.dim,self.dim,self.dim))
        featureField[:,:] = I.BACKGROUND_COLOR
        features = [(0,0,0),(1,0,0),(self.dim/2,self.dim/2,self.dim/2)]
        for x,y,z in features:
            featureField[x,y,z] = I.FEATURE_COLOR

        self.mask = DataContainer.FieldContainer(
            featureField,
            unit = '1',
            longname='String Feature',
            shortname='S')

        self.mask.seal()

    def testReturnedField(self):
        """Checking the masked field by applying a simple mask to the input field."""

        result = self.worker.createMaskedImage(self.inputField,self.mask)

        afoot = numpy.zeros((self.dim,self.dim,self.dim)).astype('d')
        afoot[0,0,0] = 0.0
        afoot[1,0,0] = numpy.sin(1.0)
        afoot[self.dim/2,self.dim/2,self.dim/2] = numpy.sin(3*round(self.dim/2))
        numpy.testing.assert_array_equal(afoot,result.data)
        assert(result.unit == self.inputField.unit)

        for resultDim,inputDim in zip(self.inputField.dimensions,
                                      result.dimensions):
            numpy.testing.assert_array_equal(resultDim.data,inputDim.data)
            assert(resultDim.unit == inputDim.unit,
                   'Units of input and output dimensions has to be equal.')

    def testReturnedTable(self):
        """Checking the extracted samples by applying a simple mask to the input field."""

        result = self.worker.findMaskPoints(self.inputField,self.mask)
        xPos = (0,1,self.dim/2)
        yPos = (0,0,self.dim/2)
        zPos = yPos
        zVal = numpy.sin(numpy.array((0,1,3.0*round(self.dim/2))))
        afoot = zip(xPos,yPos,zPos,zVal)
        table = zip(result[0].data.tolist(),
                    result[1].data.tolist(),
                    result[2].data.tolist(),
                    result[3].data.tolist())
        for row in table:
            try:
                afoot.remove(row)
            except ValueError,e:
                self.fail('Row %s not found.' % str(row))


if __name__ == '__main__':
#    suite = unittest.TestLoader().loadTestsFromName("TestApplyMask.TestApplyMask3D.testReturnedTable")
#    unittest.TextTestRunner().run(suite)
    unittest.main()

