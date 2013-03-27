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

u"""Provides unittest classes for DiffWorker
"""

__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import numpy
import pkg_resources
pkg_resources.require("pyphant")
from ImageProcessing.DiffWorker import DiffWorker
from pyphant.core.DataContainer import FieldContainer
from pyphant.quantities import Quantity


class DiffTestCase(unittest.TestCase):
    def setUp(self):
        self.fc1 = FieldContainer(
            data=numpy.array([1., 2., 5.]),
            unit=Quantity('10 m')
            )
        self.fc2 = FieldContainer(
            data=numpy.array([-2., 3., .05]),
            unit=Quantity('1 km')
            )
        self.diffWorker = DiffWorker()

    def testAbsoluteDifference(self):
        self.diffWorker.paramAbsolute.value = 'Yes'
        diff = self.diffWorker.diffImages(self.fc2, self.fc1)
        expected = FieldContainer(
            data=numpy.array([2010., 2980., .0]),
            unit=Quantity('1 m')
            )
        self.assertEqual(diff, expected)

    def testDifference(self):
        self.diffWorker.paramAbsolute.value = 'No'
        diff = self.diffWorker.diffImages(self.fc2, self.fc1)
        expected = FieldContainer(
            data=numpy.array([-2010., 2980., .0]),
            unit=Quantity('1 m')
            )
        self.assertEqual(diff, expected)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
