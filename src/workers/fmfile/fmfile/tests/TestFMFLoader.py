#!/usr/bin/env python2.5
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

# $Source$

import pkg_resources
pkg_resources.require('pyphant.fmf')

import unittest, numpy
from fmfile import FMFLoader 


class FieldContainerCondenseDim(unittest.TestCase):
    def setUp(self):
        self.x = numpy.linspace(0,0.9,10)
        m = numpy.meshgrid(self.x, self.x*5)
        self.valid = numpy.tile(self.x, (10,1))
        self.invalid = [ a.squeeze() for a in numpy.vsplit(m[0]+m[1], len(m[0])) ]

    def testInvalid(self):
        self.assertRaises(AssertionError, FMFLoader.checkAndCondense, self.invalid)

    def testValid(self):
        result = FMFLoader.checkAndCondense(self.valid)
        numpy.testing.assert_array_equal(self.x, result)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FieldContainerCondenseDim)
    unittest.TextTestRunner().run(suite)
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FieldContainerSlicing1dDim))
    #import sys
    #if len(sys.argv) == 1:
    #    unittest.main()
    #else:
    #    suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
    #    unittest.TextTestRunner().run(suite)
