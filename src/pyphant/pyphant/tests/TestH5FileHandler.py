#!/usr/bin/env python2.5
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

from __future__ import with_statement

u"""Provides unittest classes for H5FileHandler.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
from pyphant.quantities.PhysicalQuantities import Quantity as PQ
from pyphant.core.DataContainer import FieldContainer, SampleContainer,\
    assertEqual
from pyphant.core.H5FileHandler import H5FileHandler as H5FH
from numpy import array as NPArray
import os
from tempfile import mkstemp


class BasicTestCase(unittest.TestCase):
    def testReadOnlyFileNotFound(self):
        try:
            handler = H5FH('', 'r')
            assert False
        except IOError:
            pass


class FieldContainerTestCase(unittest.TestCase):
    def setUp(self):
        data = NPArray([10.0, -103.5, 1000.43, 0.0, 10.0])
        unit = PQ('3s')
        error = NPArray([0.1, 0.2, 4.5, 0.1, 0.2])
        longname = u'Test: FieldContainer H5FileHandler'
        shortname = u'TestH5FC'
        attributes = {'custom1':u'testing1...', 'custom2':u'testing2...'}
        self.fc = FieldContainer(data, unit, error, None, None, longname,
                                 shortname, attributes)
        self.fc.seal()


class FCSaveLoadTestCase(FieldContainerTestCase):
    def setUp(self):
        FieldContainerTestCase.setUp(self)
        osHandle, self.fcFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)

    def tearDown(self):
        os.remove(self.fcFilename)

    def testSaveLoad(self):
        handler = H5FH(self.fcFilename, 'w')
        with handler:
            handler.saveDataContainer(self.fc)
            fcLoaded = handler.loadDataContainer(self.fc.id)
        self.assertEqual(self.fc, fcLoaded)


class FCReadOnlyTestCase(FieldContainerTestCase):
    def setUp(self):
        FieldContainerTestCase.setUp(self)
        osHandle, self.rofcFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)
        handler = H5FH(self.rofcFilename, 'w')
        with handler:
            handler.saveDataContainer(self.fc)

    def tearDown(self):
        os.remove(self.rofcFilename)

    def testReadOnly(self):
        handler = H5FH(self.rofcFilename, 'r')
        with handler:
            fcLoaded = handler.loadDataContainer(self.fc.id)
        self.assertEqual(self.fc, fcLoaded)


class SampleContainerTestCase(unittest.TestCase):
    def setUp(self):
        data = NPArray([10.0, -103.5, 1000.43, 0.0, 10.0])
        unit = PQ('3s')
        error = NPArray([0.1, 0.2, 4.5, 0.1, 0.2])
        longname = u'Test: FieldContainer H5FileHandler'
        shortname = u'TestH5FC'
        attributes = {'custom1':u'testing1...', 'custom2':u'testing2...'}
        self.fc = FieldContainer(data, unit, error, None, None, longname,
                                 shortname, attributes)
        self.fc.seal()
        fc2 = FieldContainer(NPArray([4003.2, 5.3, 600.9]), PQ('0.2m'), None,
                             None, None, 'FieldContainer 2', 'FC2')
        fc2.seal()
        columns = [self.fc, fc2]
        longname = u'Test: SampleContainer H5FileHandler'
        shortname = u'TestH5SC'
        self.sc = SampleContainer(columns, longname, shortname, attributes)
        self.sc.seal()


class SCSaveLoadTestCase(SampleContainerTestCase):
    def setUp(self):
        SampleContainerTestCase.setUp(self)
        osHandle, self.scFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)


    def tearDown(self):
        os.remove(self.scFilename)

    def testSaveLoad(self):
        handler = H5FH(self.scFilename, 'w')
        with handler:
            handler.saveDataContainer(self.sc)
            scLoaded = handler.loadDataContainer(self.sc.id)
        self.assertEqual(self.sc, scLoaded)


class SCReadOnlyTestCase(SampleContainerTestCase):
    def setUp(self):
        SampleContainerTestCase.setUp(self)
        osHandle, self.roscFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)
        handler = H5FH(self.roscFilename, 'w')
        with handler:
            handler.saveDataContainer(self.sc)

    def tearDown(self):
        os.remove(self.roscFilename)

    def testReadOnly(self):
        handler = H5FH(self.roscFilename, 'r')
        with handler:
            scLoaded = handler.loadDataContainer(self.sc.id)
        self.assertEqual(self.sc, scLoaded)


class MixedAppendTestCase(SampleContainerTestCase):
    def setUp(self):
        SampleContainerTestCase.setUp(self)
        osHandle, self.appscFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)
        handler = H5FH(self.appscFilename, 'w')
        with handler:
            handler.saveDataContainer(self.fc)

    def tearDown(self):
        os.remove(self.appscFilename)

    def testAppend(self):
        handler = H5FH(self.appscFilename, 'a')
        with handler:
            handler.saveDataContainer(self.sc)
            fcLoaded = handler.loadDataContainer(self.fc.id)
            scLoaded = handler.loadDataContainer(self.sc.id)
        self.assertEqual(self.fc, fcLoaded)
        self.assertEqual(self.sc, scLoaded)


class SummaryTestCase(SampleContainerTestCase):
    def setUp(self):
        SampleContainerTestCase.setUp(self)
        osHandle, self.summFilename = mkstemp(suffix = '.h5',
                                            prefix = 'pyphantH5FileHandlerTest')
        os.close(osHandle)
        handler = H5FH(self.summFilename, 'w')
        with handler:
            handler.saveDataContainer(self.sc)

    def tearDown(self):
        os.remove(self.summFilename)

    def testSummary(self):
        handler = H5FH(self.summFilename, 'r')
        with handler:
            summarydict = handler.loadSummary()
        scsummary = summarydict[self.sc.id]
        fcsummary = summarydict[self.fc.id]
        self.assertEqual(scsummary['id'], self.sc.id)
        self.assertEqual(fcsummary['id'], self.fc.id)
        self.assertEqual(scsummary['longname'], self.sc.longname)
        self.assertEqual(fcsummary['longname'], self.fc.longname)
        self.assertEqual(scsummary['shortname'], self.sc.shortname)
        self.assertEqual(fcsummary['shortname'], self.fc.shortname)
        self.assertEqual(scsummary['creator'], self.sc.creator)
        self.assertEqual(fcsummary['creator'], self.fc.creator)
        self.assertEqual(scsummary['machine'], self.sc.machine)
        self.assertEqual(fcsummary['machine'], self.fc.machine)
        self.assertEqual(scsummary['attributes'], self.sc.attributes)
        self.assertEqual(fcsummary['attributes'], self.fc.attributes)
        self.assertEqual(fcsummary['unit'], self.fc.unit)
        self.assertEqual(scsummary['columns'][0]['dimensions'][0],
                         summarydict[self.fc.dimensions[0].id])
        self.assertEqual(scsummary['columns'][0], fcsummary)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
