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

"""
This module provides a wrapper class that translates the
KnowledgeManager's summary dictionaries to an SQLite3 database.
"""
__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$:

import sqlite3
import time
from pyphant.core.Helpers import (utf82uc, uc2utf8, emd52dict)
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity
from types import (FloatType, IntType, LongType, StringTypes)

def quantity2dbase(quantity):
    if isinstance(quantity, PhysicalQuantity):
        return (quantity.value, quantity.getUnitName(),
                tuple(quantity.unit.powers))
    elif isinstance(quantity, (FloatType, IntType, LongType)):
        return (quantity, None, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    else:
        raise ValueError("Expected (PhysicalQuantity, FloatType, IntType, "\
                             "LongType) but got %s instead."\
                             % (type(quantity), ))

def dbase2quantity(dbase):
    if dbase[1] == None:
        return dbase[0]
    else:
        return PhysicalQuantity(dbase[0], uc2utf8(dbase[1]))

def date2dbase(date):
    """extends a short datestring to YYYY-MM-DD_hh:mm:ss.ssssss standard
    """
    assert len(date) in [4, 7, 10, 13, 16, 19, 21, 22, 23, 24, 25, 26]
    date = date.replace(' ', '_')
    complete_str = '0000-01-01_00:00:00.000000'
    return date + complete_str[len(date):]

def emd52type(emd5):
    if emd5.endswith('d'):
        return 'fc'
    elif emd5.endswith('e'):
        return 'sc'
    else:
        raise ValueError(emd5)

def replace_type(str, type):
    if type == 'field':
        return str % ('fc', )
    elif type == 'sample':
        return str % ('sc', )

def get_wildcards(length, char, braces=False, commas=True):
    if braces:
        wc = '('
    else:
        wc = ''
    for index in xrange(length):
        wc += char
        if commas:
            wc += ','
        wc += ' '
    if commas:
        wc = wc[:-2]
    else:
        wc = wc[:-1]
    if braces:
        wc += ')'
    return wc

class SQLiteWrapper(object):
    """Wrapper class for DC meta data <-> sqlite3
    """
    common_keys = ['longname', 'shortname', 'machine',
                   'creator', 'hash', 'date']
    writable_keys = ['storage']
    fast_keys = ['machine', 'creator', 'date', 'hash', 'type', 'id']
    all_keys = ['id', 'hash', 'longname', 'shortname', 'machine', 'creator',
                'date', 'type', 'attributes', 'storage', 'unit', 'columns',
                'dimensions']
    common_result_keys = common_keys + ['id', 'type', 'attributes', 'storage']
    fc_result_keys = common_result_keys + ['unit', 'dimensions']
    sc_result_keys = common_result_keys + ['columns']
    fc_spec_res_keys = ['unit', 'dimensions', 'attributes']
    sc_spec_res_keys = ['columns', 'attributes']
    one_to_one_search_keys = ['longname', 'shortname', 'machine',
                              'creator', 'hash', 'storage']
    one_to_one_result_keys = one_to_one_search_keys + ['date', 'id', 'type']
    common_search_keys = one_to_one_search_keys + ['id', 'attributes',
                                                   'date_from', 'date_to']
    sortable_keys = common_keys + ['id', 'storage', 'type']

    def __init__(self, database, timeout=60.0):
        """
        Arguments:
        - database: database to connect to
        """
        self.database = database
        self.timeout = timeout
        self.connection = None
        self.cursor = None

    def __enter__(self):
        assert self.connection == None
        assert self.cursor == None
        self.connection = sqlite3.connect(self.database, self.timeout)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        if type == None:
            try:
                self.connection.commit()
            except:
                print "Could not commit changes to database."
        if hasattr(self.cursor, 'close'):
            self.cursor.close()
        if hasattr(self.connection, 'close'):
            self.connection.close()
        self.cursor = None
        self.connection = None

    def __getitem__(self, emd5):
        if self.has_entry(emd5):
            if emd5.endswith('field'):
                return FCRowWrapper(emd5, self.cursor)
            elif emd5.endswith('sample'):
                return SCRowWrapper(emd5, self.cursor)
        raise KeyError(emd5)

    def setup_dbase(self):
        def createTable(table_name, columns, cursor):
            query = "CREATE TABLE IF NOT EXISTS %s (" % (table_name, )
            for name, type in columns:
                query += name + " " + type + ", "
            query = query[:-2] + ")"
            cursor.execute(query)
        def createTrigger(trigger_name, action, table_name,
                          statements, cursor):
            query = "CREATE TRIGGER IF NOT EXISTS %s AFTER %s ON %s "\
                "FOR EACH ROW BEGIN %s END"
            st_query = ''
            for st in statements:
                st_query += st + ';'
            cursor.execute(query % (trigger_name, action,
                                    table_name, st_query))
        #create tables:
        columns = [('sc_id', 'TEXT PRIMARY KEY UNIQUE NOT NULL'),
                   ('longname', 'TEXT'),
                   ('shortname', 'TEXT'),
                   ('machine', 'TEXT'),
                   ('creator', 'TEXT'),
                   ('date', 'TEXT'),
                   ('hash', 'TEXT'),
                   ('storage', 'TEXT')]
        createTable("km_sc", columns, self.cursor)
        columns[0] = ('fc_id', 'TEXT PRIMARY KEY UNIQUE NOT NULL')
        columns.insert(7, ('unit_value', ''))
        columns.insert(8, ('unit_name', 'TEXT'))
        columns.insert(9, ('bu_id', 'INT'))
        createTable("km_fc", columns, self.cursor)
        columns = [('sc_id', 'TEXT NOT NULL'),
                   ('fc_id', 'TEXT NOT NULL'),
                   ('fc_index', 'INT NOT NULL'),
                   ('', 'UNIQUE(sc_id, fc_id, fc_index)'),
                   ('', 'PRIMARY KEY(sc_id, fc_id, fc_index)')]
        createTable("km_sc_columns", columns, self.cursor)
        columns = [('fc_id', 'TEXT NOT NULL'),
                   ('dim_id', 'TEXT NOT NULL'),
                   ('dim_index', 'INT NOT NULL'),
                   ('', 'UNIQUE(fc_id, dim_id, dim_index)'),
                   ('', 'PRIMARY KEY(fc_id, dim_id, dim_index)')]
        createTable("km_fc_dimensions", columns, self.cursor)
        columns = [('dc_id', 'TEXT NOT NULL'),
                   ('key', 'TEXT NOT NULL'),
                   ('value', 'TEXT'),
                   ('', 'UNIQUE(dc_id, key)'),
                   ('', 'PRIMARY KEY(dc_id, key)')]
        createTable('km_attributes', columns, self.cursor)
        columns = [('dc_id', 'TEXT PRIMARY KEY UNIQUE NOT NULL')]
        createTable("km_temporary", columns, self.cursor)
        columns = [('bu_id', 'INTEGER PRIMARY KEY AUTOINCREMENT '\
                        'NOT NULL UNIQUE'),
                   ('m', 'INT'),
                   ('g', 'INT'),
                   ('s', 'INT'),
                   ('A', 'INT'),
                   ('K', 'INT'),
                   ('mol', 'INT'),
                   ('cd', 'INT'),
                   ('rad', 'INT'),
                   ('sr', 'INT'),
                   ('EUR', 'INT'),
                   ('', 'UNIQUE(m, g, s, A, K, mol, cd, rad, sr, EUR)')]
        createTable('km_base_units', columns, self.cursor)
        #create triggers:
        createTrigger('trigger_del_fc', 'DELETE', 'km_fc',
                      ['DELETE FROM km_attributes WHERE dc_id=OLD.fc_id',
                       'DELETE FROM km_fc_dimensions WHERE fc_id=OLD.fc_id'],
                      self.cursor)
        createTrigger('trigger_del_sc', 'DELETE', 'km_sc',
                      ['DELETE FROM km_attributes WHERE dc_id=OLD.sc_id',
                       'DELETE FROM km_sc_columns WHERE sc_id=OLD.sc_id'],
                      self.cursor)
        createTrigger('trigger_del_tmp', 'DELETE', 'km_temporary',
                      ['DELETE FROM km_fc WHERE fc_id=OLD.dc_id',
                       'DELETE FROM km_sc WHERE sc_id=OLD.dc_id'],
                      self.cursor)
        #clean tmp:
        self.cursor.execute("DELETE FROM km_temporary")

    def has_entry(self, id):
        exe = self.cursor.execute
        type = emd52type(id)
        exe("SELECT %s_id FROM km_%s WHERE %s_id=?" % (type, type, type),
            (id, ))
        return self.cursor.fetchone() != None

    def _set_fc_keys(self, insert_dict, summary):
        exe = self.cursor.execute
        insert_dict['fc_id'] = summary['id']
        q2db = quantity2dbase(summary['unit'])
        insert_dict['unit_value'] = q2db[0]
        insert_dict['unit_name'] = q2db[1]
        try:
            exe("INSERT OR ABORT INTO km_base_units "\
                    "(m, g, s, A, K, mol, cd, rad, sr, EUR) "\
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", q2db[2])
            l_row_id = self.cursor.lastrowid
        except sqlite3.IntegrityError:
            exe("SELECT bu_id FROM km_base_units WHERE m=? AND g=? "\
                    "AND s=? AND A=? AND K=? AND mol=? AND cd=? AND rad=? "\
                    "AND sr=? AND EUR=?", q2db[2])
            tmp = self.cursor.fetchone()
            assert tmp != None
            l_row_id = tmp[0]
        insert_dict['bu_id'] = l_row_id
        dimension_query = "INSERT INTO km_fc_dimensions VALUES (?, ?, ?)"
        if summary['dimensions'] != [u'IndexMarker']:
            for dim_id, dim_index in zip(summary['dimensions'],
                                         range(len(summary['dimensions']))):
                exe(dimension_query, (summary['id'], dim_id, dim_index))

    def set_entry(self, summary, storage, temporary=False):
        """Sets the meta data in the database according to the
        summary dictionary. If the according entry already exists,
        the database is not changed since the same emd5s should always
        reference the same (meta)data.
        Arguments:
        - summary: dictionary with meta data
        - storage: string type (e.g. path in local file system)
        - temporary: Flag that marks data to be deleted upon next
                     call to setup_dbase().
        """
        if self.has_entry(summary['id']):
            return
        exe = self.cursor.execute
        if temporary:
            exe("INSERT INTO km_temporary VALUES (?)",
                (summary['id'],))
        insert_dict = dict([(key, value) for key, value in \
                                summary.iteritems() if key in \
                                SQLiteWrapper.common_keys])
        insert_dict['storage'] = storage
        insert_dict['date'] = date2dbase(insert_dict['date'])
        type = emd52type(summary['id'])
        attr_query = "INSERT INTO km_attributes VALUES (?, ?, ?)"
        for key, value in summary['attributes'].iteritems():
            assert isinstance(key, StringTypes)
            exe(attr_query, (summary['id'], key, value.__repr__()))
        if type == 'fc':
            self._set_fc_keys(insert_dict, summary)
        else:
            insert_dict['sc_id'] = summary['id']
            column_query = "INSERT INTO km_sc_columns VALUES (?, ?, ?)"
            for fc_id, fc_index in zip(summary['columns'],
                                       range(len(summary['columns']))):
                exe(column_query, (summary['id'], fc_id, fc_index))
        insert_query = "INSERT INTO km_%s %s VALUES %s"
        value_list = []
        key_query = "("
        value_query = "("
        for key, value in insert_dict.iteritems():
            value_query += "?, "
            key_query += key + ", "
            value_list.append(value)
        key_query = key_query[:-2] + ")"
        value_query = value_query[:-2] + ")"
        insert_query = insert_query % (type, key_query, value_query)
        exe(insert_query, tuple(value_list))

    def get_emd5_list(self):
        self.cursor.execute("SELECT fc_id FROM km_fc")
        emd5_list = self.cursor.fetchall()
        self.cursor.execute("SELECT sc_id FROM km_sc")
        emd5_list.extend(self.cursor.fetchall())
        return [row[0] for row in emd5_list]

    def verify_keys(self, keys, allowed):
        for key in keys:
            if not key in allowed:
                raise KeyError(key)

    def translate_result_key(self, key, type):
        if type == 'field':
            trans_keys = self.fc_spec_res_keys
        elif type == 'sample':
            trans_keys = self.sc_spec_res_keys
        if key in trans_keys:
            return 'NULL'
        elif key == 'id':
            return replace_type("%s_id", type)
        elif key == 'type':
            return "'%s' AS type" % type
        else:
            return key

    def translate_search_dict(self, type, search_dict):
        where = ''
        values = []
        for key, value in search_dict.iteritems():
            if key in self.one_to_one_search_keys:
                expr = '%s=?' % key
            elif key == 'id':
                expr = '%s=?' % replace_type('%s_id', type)
            elif key == 'date_from':
                expr = 'date>=?'
                value = date2dbase(value)
            elif key == 'date_to':
                expr = 'date<?'
                value = date2dbase(value)
            else:
                #TODO
                raise NotImplementedError(key)
            where += expr + " AND "
            values.append(value)
        return where[:-5], values

    def translate_row(self, idrow, result_keys):
        id = idrow[0]
        row = list(idrow[1:])
        index = 0
        for key, value in zip(result_keys, row):
            if key in self.one_to_one_result_keys:
                pass
            else:
                raise NotImplementedError(key)
            index += 1
        return tuple(row)

    def get_andsearch_query(self, type, result_keys, search_dict, distinct):
        trans_res_keys = tuple([self.translate_result_key(key, type) \
                                    for key in ['id'] + result_keys])
        if type == 'field':
            table = 'km_fc'
        elif type == 'sample':
            table = 'km_sc'
        if search_dict == {}:
            qry = "SELECT %s %s FROM %s "
            values = None
        else:
            qry = "SELECT %s FROM %s WHERE "
        qry = (qry % (get_wildcards(len(trans_res_keys), '%s'), table)) \
            % trans_res_keys
        if search_dict != {}:
            where, values = self.translate_search_dict(type, search_dict)
            qry += where
        return qry, values

    def get_andsearch_result(self, result_keys, search_dict={},
                             order_by=None, order_asc=True,
                             limit=-1, offset=0, distinct=False):
        """returns a list of tuples filled with values of the result keys
        matching the constraints of search_dict.
        Arguments:
        - result_keys: List (of length >= 1) of keys to include in the
          result tuples. Be sure not to mix FC only and SC only keys.
        - search_dict: Dict mapping keys to constraint values.
          Use empty dict for no constraints at all
          possible keys: values (used relational operator[, type constraint]):
          'longname': str types (==)
          'shortname': str types (==)
          'machine': str types (==)
          'creator: str types (==)
          'date_from:' str types:
                       YYYY[-MM[-DD[_hh:[mm:[ss[.s[s[s[s[s[s]]]]]]]]]]] (>=)
          'date_to:' str types:
                     YYYY[-MM[-DD[_hh:[mm:[ss[.s[s[s[s[s[s]]]]]]]]]]] (<)
          'hash': str types (==)
          'id': str types: emd5 (==)
          'type': 'field' or 'sample' (==)
          'attributes': dict mapping attr. key to attr. value (==)
          'storage': str types (==)
          'unit': PhysicalUnit or int: 1 (==, FC only)
          'dimensions': list of FC search dicts
                        (see above definitions, FC only)
          'columns': list of FC search dicts (see above definitions, SC only)
        - order_by: element of result_keys to order the results by
                    or None for no special ordering
        - order_asc: whether to order ascending
        - limit: maximum number of results to return,
          set to -1 for no limit, default: -1
        - offset: number of search results to skip, default: 0
        - distinct: flag that indicates whether the result list
          should only contain distinct tuples.
        Usage Examples:
        Get list of all longnames:
           get_andsearch_result(['longname'], distinct=True)
           --> [('name1', ), ('name2', ), ...]
        Get id and shortname of all 1d FCs that are parametrized by
        a time dimension:
           tunit = PhysicalQuantity(1, 's').unit
           get_andsearch_result(['id', 'shortname'],
                                {'type':'field',
                                 'dimensions':[{'unit':tunit}]})
           --> [('emd5_1', 'name_1'), ('emd5_2', 'name_2'), ...]
        """
        if order_by == None:
            order = ''
        else:
            assert order_by in result_keys
            assert order_by in self.sortable_keys
            order = ' ORDER BY %s' % order_by
            if order_asc:
                order += ' ASC'
            else:
                order += ' DESC'
        assert isinstance(limit, int)
        assert isinstance(offset, int)
        if not search_dict.has_key('type'):
            self.verify_keys(result_keys, self.common_result_keys)
            self.verify_keys(search_dict.keys(), self.common_search_keys)
            fc_query, fc_values \
                = self.get_andsearch_query('field', result_keys,
                                           search_dict, distinct)
            sc_query, sc_values \
                = self.get_andsearch_query('sample', result_keys,
                                           search_dict, distinct)
            query = "%s UNION ALL %s%s LIMIT %d OFFSET %d"
            query = query % (fc_query, sc_query, order, limit, offset)
            if search_dict != {}:
                self.cursor.execute(query, fc_values + sc_values)
            else:
                self.cursor.execute(query)
        rows = [self.translate_row(row, result_keys) for row in self.cursor]
        if distinct:
            return list(set(rows))
        else:
            return rows


class RowWrapper(object):

    def __init__(self, emd5, cursor, type):
        self.cursor = cursor
        self.emd5 = emd5
        self.emd5dict = emd52dict(emd5)
        self.emd5dict['id'] = emd5
        self.select_query = "SELECT %s FROM km_%s WHERE %s_id=?"\
            % ('%s', type, type)
        self.update_query = "UPDATE km_%s SET %s=? WHERE %s_id=?"\
            % (type, '%s', type)
        self.attr_query = "SELECT key, value FROM km_attributes WHERE dc_id=?"

    def __getitem__(self, key):
        if not key in SQLiteWrapper.all_keys:
            raise ValueError("'%s' is not a valid key!" % (key, ))
        elif key in SQLiteWrapper.fast_keys:
            return self.emd5dict[key]
        elif key == 'attributes':
            self.cursor.execute(self.attr_query, (self.emd5, ))
            # Eval is evil! TODO: Nail possible types of avalue and write
            # according wrappers.
            return dict([(akey, eval(avalue)) for akey, avalue in self.cursor])
        else:
            self.cursor.execute(self.select_query % (key, ), (self.emd5, ))
            return self.cursor.fetchone()[0]

    def __setitem__(self, key, value):
        if key not in SQLiteWrapper.writable_keys:
            raise ValueError("'%s' is read only!" % (key, ))
        else:
            self.cursor.execute(self.update_query % (key, ),
                                (value, self.emd5))


class FCRowWrapper(RowWrapper):

    def __init__(self, emd5, cursor):
        RowWrapper.__init__(self, emd5, cursor, 'fc')
        self.dimension_query = "SELECT dim_id FROM km_fc_dimensions "\
            "WHERE fc_id=? ORDER BY dim_index ASC"
        self.unit_query = "SELECT unit_value, unit_name FROM km_fc "\
            "WHERE fc_id=?"

    def __getitem__(self, key):
        if key == 'unit':
            self.cursor.execute(self.unit_query, (self.emd5, ))
            return dbase2quantity(self.cursor.fetchone())
        elif key == 'dimensions':
            self.cursor.execute(self.dimension_query, (self.emd5, ))
            dimensions = [row[0] for row in self.cursor]
            if dimensions == []:
                dimensions = [u'IndexMarker']
            return dimensions
        elif key == 'columns':
            raise KeyError(key)
        else:
            return RowWrapper.__getitem__(self, key)


class SCRowWrapper(RowWrapper):

    def __init__(self, emd5, cursor):
        RowWrapper.__init__(self, emd5, cursor, 'sc')
        self.column_query = "SELECT fc_id FROM km_sc_columns "\
            "WHERE sc_id=? ORDER BY fc_index ASC"

    def __getitem__(self, key):
        if key == 'columns':
            self.cursor.execute(self.column_query, (self.emd5, ))
            return [row[0] for row in self.cursor]
        elif key == 'unit' or key == 'dimensions':
            raise KeyError(key)
        else:
            return RowWrapper.__getitem__(self, key)
