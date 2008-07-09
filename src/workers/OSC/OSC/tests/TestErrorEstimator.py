# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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

u"""Provides unittest class TestErrorEstimation.
"""

__id__ = "$Id$"
__author__ = "$Author: obi $"
__version__ = "$Revision: 4164 $"
# $Source$


import sys
import unittest
import pkg_resources

pkg_resources.require("pyphant")
pkg_resources.require("pyphant_osc")

import numpy
import OSC.ErrorEstimator as OE

class TestLocalNoise(unittest.TestCase):
    """Tests the estimation of local noise on basis of sample standard deviations."""
    def setUp(self):
        self.data = numpy.arange(10).astype('float')

    def testLinearOddSamples(self):
        """Tests the correct computation of sample standard deviation for a straight line with an odd number of samples."""
        expected = numpy.resize(1.0,self.data.shape)
        stdRand = numpy.sqrt((2.0*(1.0-2.0/3)**2+4.0/9.0)*0.5)
        expected[0] = stdRand
        expected[-1]= stdRand
        result = OE.localNoise(self.data,samples=3)

        numpy.testing.assert_array_almost_equal(expected,result,err_msg='Expected local noise is %s, but should be %s.' % (result,expected))

    def testLinearEvenSamples(self):
        """Tests the correct computation of sample standard deviation for a straight line with an even set of samples.
        """
        std = numpy.sqrt(5./3)
        expected = numpy.resize(std,self.data.shape)
        stdRand = numpy.sqrt(2./3)
        expected[:2] = stdRand
        expected[-1:]= stdRand
        result = OE.localNoise(self.data,samples=4)

        numpy.testing.assert_array_almost_equal(expected,result,err_msg='Expected local noise is %s, but should be %s.' % (result,expected))

if __name__ == '__main__':
    unittest.main()
