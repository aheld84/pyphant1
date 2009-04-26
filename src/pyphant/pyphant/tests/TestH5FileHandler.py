#!/usr/bin/env python2.5
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

u"""Provides unittest classes for H5FileHandler.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity as PQ
from pyphant.core.DataContainer import FieldContainer,SampleContainer,assertEqual
from pyphant.core.H5FileHandler import H5FileHandler as H5FH
from numpy import array as NPArray
import os
from tempfile import mkstemp

class TestData(unittest.TestCase):
    def setUp(self):
        data = NPArray([10.0, -103.5, 1000.43, 0.0, 10.0])
        unit = PQ('3s')
        error = NPArray([0.1, 0.2, 4.5, 0.1, 0.2])
        longname = u'Test: FieldContainer H5FileHandler'
        shortname = u'TestH5'
        attributes = {u'custom1':u'testing1...', u'custom2':'testing2...'}
        self.fc = FieldContainer(data, unit, error, None, None, longname, shortname, attributes)
        self.fc.seal()
        osHandle, self.tmpFilename = mkstemp(prefix='pyphantH5FileHandlerTest')
        os.close(osHandle)

    def tearDown(self):
        os.remove(self.tmpFilename)


class BasicTestCase(unittest.TestCase):
    def testReadOnlyFileNotFound(self):
        try:
            handler = H5FH('', True)
            assert False
        except IOError:
            pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
