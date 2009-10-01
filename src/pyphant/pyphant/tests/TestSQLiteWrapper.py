#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""Provides unittest classes for SQLiteWrapper.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
import pyphant.core.SQLiteWrapper


class SQLiteWrapperTestCase(unittest.TestCase):
    def setUp(self):
        import tempfile
        import os
        self.dir = tempfile.mkdtemp()
        self.dbase = self.dir + os.path.sep + "testcase.sqlite3"
        self.wrapper = pyphant.core.SQLiteWrapper.SQLiteWrapper(self.dbase)
        with self.wrapper:
            self.wrapper.setup_dbase()
        from pyphant.quantities.PhysicalQuantities import PhysicalQuantity
        self.summary = {'id':'emd5://PC/aheld/'
                        '2009-01-01_12:00:00.123456/12345678910.field',
                        'longname':'name',
                        'shortname':'sn', 'creator':'aheld',
                        'date':'2009-01-01_12:00:00.123456',
                        'machine':'PC', 'type':'field',
                        'unit':PhysicalQuantity('10.03e-8 mm**-1'),
                        'attributes':{'attribute1':'bla1',
                                      'attribute2':'bla2'},
                        'hash':'12345678910'}
        self.sc_summary = self.summary.copy()
        self.sc_summary['id'] = self.summary['id'][:-5] + 'sample'
        self.sc_summary.pop('unit')
        self.sc_summary['columns'] = [self.summary['id'], 'dummy']
        self.sc_summary['type'] = 'sample'

    def tearDown(self):
        import os
        os.remove(self.dbase)
        os.removedirs(self.dir)

    def testAll(self):
        with self.wrapper:
            id = self.summary['id']
            assert not self.wrapper.has_entry(id)
            self.wrapper.set_entry(self.summary, 'storage1')
            assert self.wrapper.has_entry(id)
            rowwrapper = self.wrapper[id]
            for key, value in self.summary.iteritems():
                assert value == rowwrapper[key]
            assert rowwrapper['storage'] == 'storage1'
            rowwrapper['storage'] = 'storage2'
            assert rowwrapper['storage'] == 'storage2'
            try:
                bad = rowwrapper['bad']
                assert False
            except ValueError:
                pass
            self.wrapper.set_entry(self.summary, 'storage3')
            assert rowwrapper['storage'] == 'storage2'
            self.wrapper.set_entry(self.sc_summary, 'storage4')
            rowwrapper = self.wrapper[self.sc_summary['id']]
            assert rowwrapper['columns'] == self.sc_summary['columns']
            emd5list = self.wrapper.get_emd5_list()
            assert len(emd5list) == 2
            assert self.summary['id'] in emd5list
            assert self.sc_summary['id'] in emd5list


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
