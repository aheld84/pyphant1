#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010, Rectorate of the University of Freiburg
# Copyright (c) 2010, Andreas W. Liehr (liehr@users.sourceforge.net)
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

u"""Provides unittest classes for SQLiteWrapper.
"""

__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
import pyphant.core.SQLiteWrapper
from pyphant.quantities import Quantity
from pyphant.core.H5FileHandler import (im_id, im_summary)

class TestQuantity2powers(unittest.TestCase):
    def testPowersOfUnits(self):
        expected = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        result = pyphant.core.SQLiteWrapper.quantity2powers(Quantity('1m'))
        self.assertEqual(expected,result,"The number of basic units determining a quantity does not fit. The SQTLiteWrapper is expecting")
        
    def testChangedBaseUnits(self):
        """Test if function quantity2powers checks the expected number of unit powers as given by Quantity.unit.powers
        in order to avoid clashes with the SQLite tables."""
        class Unit:
            powers = (1, 0, 0)
        class fakedQuantity:
            """Faked Quantity class of TestQuantity2powers unittest."""
            def __init__(self):
                self.unit = Unit()
                self.__class__ = Quantity
        quantity = fakedQuantity()
        self.assertRaises(AssertionError,pyphant.core.SQLiteWrapper.quantity2powers,quantity)

class SQLiteWrapperTestCase(unittest.TestCase):
    def setUp(self):
        import tempfile
        import os
        self.dir = tempfile.mkdtemp()
        self.dbase = self.dir + os.path.sep + "testcase.sqlite3"
        self.wrapper = pyphant.core.SQLiteWrapper.SQLiteWrapper(self.dbase)
        with self.wrapper:
            self.wrapper.setup_dbase()
        self.summary = {'id':'emd5://PC/aheld/'
                        '2009-01-01_12:00:00.123456/12345678910.field',
                        'longname':'name',
                        'shortname':'sn', 'creator':'aheld',
                        'date':'2009-01-01_12:00:00.123456',
                        'machine':'PC', 'type':'field',
                        'unit':Quantity('10.03e-8 mm**-1'),
                        'attributes':{'attribute1':'bla1',
                                      'attribute2':'bla2'},
                        'hash':'12345678910',
                        'dimensions':[im_id]}
        self.sc_summary = self.summary.copy()
        self.sc_summary['id'] = self.summary['id'][:-5] + 'sample'
        self.sc_summary.pop('unit')
        self.sc_summary.pop('dimensions')
        self.sc_summary['columns'] = [self.summary['id'], self.summary['id']]
        self.sc_summary['type'] = 'sample'
        self.sc_summary['longname'] = u'name2'
        self.sc_summary['shortname'] = u'sn2'

    def tearDown(self):
        import os
        os.remove(self.dbase)
        os.removedirs(self.dir)

    def testAll(self):
        assert pyphant.core.SQLiteWrapper.date2dbase('2009') \
            == '2009-01-01_00:00:00.000000'
        with self.wrapper:
            id = self.summary['id']
            assert not self.wrapper.has_entry(id)
            self.wrapper.set_entry(im_summary, None)
            assert self.wrapper.has_entry(im_summary['id'])
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
            assert len(emd5list) == 3
            assert self.summary['id'] in emd5list
            assert self.sc_summary['id'] in emd5list
            keys = self.wrapper.common_result_keys
            dictionary = self.summary.copy()
            dictionary.pop('date')
            dictionary.pop('dimensions')
            dictionary.pop('unit')
            dictionary.pop('type')
            dictionary.pop('attributes')
            dictionary['storage'] = 'storage2'
            dictionary['date_from'] = u'2009-01-01_12:00:00.000000'
            dictionary['date_to'] = u'2009-01-01_12:00:00.200000'
            search_result = self.wrapper.get_andsearch_result(
                keys, dictionary, order_by='type', limit=10, offset=0)
            assert len(search_result) == 1
            expected = [(u'name', u'sn', u'PC', u'aheld', u'12345678910',
                         u'2009-01-01_12:00:00.123456', u'emd5://PC/aheld/'\
                             u'2009-01-01_12:00:00.123456/12345678910.field',
                         u'field', u'storage2')]
            assert search_result == expected
            dictionary['type'] = 'field'
            search_result = self.wrapper.get_andsearch_result(keys, dictionary)
            assert search_result == expected
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], order_by='longname')
            assert search_result == [(u'index', ), (u'name', ), (u'name2', )]
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'unit':Quantity(20, '1/m'),
                               'type':'field'})
            assert search_result == [(u'name', )]
            search_result = self.wrapper.get_andsearch_result(
                ['unit'], {'type':'field', 'longname':'name'})
            assert search_result == [(Quantity('10.03e-8 mm**-1'), )]
            search_result = self.wrapper.get_andsearch_result(
                ['latex_unit'], {'type':'field', 'longname':'name'})
            #assert search_result == [(..., )]
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'attributes':{'attribute2':'bla2'}},
                order_by='longname')
            assert search_result == [(u'name', ), (u'name2', )]
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'attributes':{'attribute2':'bla2',
                                             'attribute1':'bla1'}},
                order_by='longname')
            assert search_result == [(u'name', ), (u'name2', )]
            any_value = self.wrapper.any_value
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'attributes':{'attribute1':any_value,
                                             'attribute2':'bla2'}})
            assert search_result == [(u'name', ), (u'name2', )]
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'type':'sample',
                               'columns':[{'unit':Quantity(2.0, '1/m')}
                                          , {}]})
            assert search_result == [(u'name2', )]
            search_result = self.wrapper.get_andsearch_result(
                ['longname'],
                {'type':'field',
                 'dimensions':[{'longname':im_summary['longname']}],
                 'longname':self.summary['longname']})
            assert search_result == [(u'name', )]
            rowwrapper = self.wrapper[id]
            assert rowwrapper['dimensions'] == self.summary['dimensions']
            search_result = self.wrapper.get_andsearch_result(
                ['longname'], {'type':'field', 'dim_of':{'id':id}})
            assert search_result == [(im_summary['longname'], )]
            search_result = self.wrapper.get_andsearch_result(
                ['shortname'], {'type':'field',
                                'col_of':{'id':self.sc_summary['id']}})
            assert search_result == [(self.summary['shortname'], )]


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
