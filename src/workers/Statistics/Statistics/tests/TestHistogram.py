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

u"""Provides unittest class TestHistogram.
"""

__version__ = "$Revision:$"
# $Source$

import sys
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("pyphant")

import Statistics.Histogram as S
import numpy
import scipy.special
from pyphant.core import DataContainer

dim = 100000
uniformSample = numpy.random.uniform(size=dim)
normalSample  = numpy.random.normal(size=dim)

class TestHistogram(unittest.TestCase):
    """Tests the correct computation of histograms from SampleContainers."""
    def setUp(self):
        self.dim = dim
        self.worker = S.Histogram(None)
        self.accuracyLevel = -3
        self.uniform = DataContainer.FieldContainer(
            uniformSample,
            unit = '1 V',
            longname='Uniform noise',
            shortname='g' )
        self.norm = DataContainer.FieldContainer(
            normalSample,
            unit = '1 V',
            longname='Gaussian white noise',
            shortname='w' )
        self.uniform.seal()

    def testUniform(self):
        """Tests the correct evaluation of a uniform noise sample."""
        result   = self.worker.calculateHistogram(self.uniform)
        bins     = self.worker.getParam('bins').value
        afoot    = numpy.zeros((bins,)).astype('d')
        afoot[:] = self.dim / bins
        self.assertEqual(result.data.sum(),self.dim,
                         'Number of counts has to match number of samples.')
        numpy.testing.assert_almost_equal(afoot,
                                          result.data,
                                          decimal=self.accuracyLevel)
        self.failUnless(result.dimensions[0].unit == self.uniform.unit,
                        "Unit of result's dimension [%s] has to match "
                        "the unit of the input data [%s]."
                        % (result.dimensions[0].unit, self.uniform.unit))

    def testNormal(self):
        """Tests the correct evaluation of a Gaussian white noise sample."""
        self.worker.getParam('bins').value=20
        result = self.worker.calculateHistogram(self.norm)
        sample = numpy.linspace(numpy.floor(self.norm.data.min()),
                                numpy.ceil(self.norm.data.max()),
                                result.data.size+1)
        bins = self.worker.getParam('bins').value
        def GaussErrInt(x):
            return 0.5*(1.0+scipy.special.erf(x/numpy.sqrt(2.0)))
        erf = GaussErrInt(sample)
        afoot = numpy.zeros((bins,)).astype('d')
        afoot = erf[1:]-erf[:-1]
        afoot *= self.dim
        self.assertEqual(result.data.sum(),self.dim,
                         'Number of counts has to match number of samples.')
        numpy.testing.assert_almost_equal(afoot,
                                          result.data,
                                          decimal=self.accuracyLevel)
        self.failUnless(result.dimensions[0].unit == self.norm.unit,
                        "Unit of result's dimension [%s] has to match "
                        "the unit of the input data [%s]."
                        % (result.dimensions[0].unit, self.norm.unit))

if __name__ == '__main__':
    unittest.main()
