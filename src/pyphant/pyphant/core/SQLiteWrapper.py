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
KnowledgeManager's summary dictionaries to an SQLite3 databasae.
"""
__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$:

import sqlite3
import time
from pyphant.core.Helpers import (utf82uc, emd52dict)
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity
from types import (FloatType, IntType, LongType, StringTypes)

def quantity2dbase(quantity):
    if isinstance(quantity, PhysicalQuantity):
        return quantity.__repr__()
    elif isinstance(quantity, (FloatType, IntType, LongType)):
        return quantity
    else:
        raise ValueError("Expected (PhysicalQuantity, FloatType, IntType, "\
                             "LongType) but got %s instead."\
                             % (type(quantity), ))

def dbase2quantity(dbase):
    if isinstance(dbase, StringTypes):
        assert dbase.startswith("PhysicalQuantity(")
        tmp = dbase.split('(')[1].split(',')
        try:
            value = int(tmp[0])
        except ValueError:
            value = float(tmp[0])
        return PhysicalQuantity(value, tmp[1][1:-2])
    elif isinstance(dbase, (FloatType, IntType, LongType)):
        return dbase
    else:
        raise ValueError("Broken FC unit in dbase: %s" % (dbase.__repr__(), ))

def date2dbase(date):
    """converts a pyphant datestring to sql standard
    """
    return date.replace("_", " ")[:23]

def emd52type(emd5):
    if emd5.endswith('d'):
        return 'fc'
    elif emd5.endswith('e'):
        return 'sc'
    else:
        raise ValueError(emd5)


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
        columns = [('sc_id', 'TEXT PRIMARY KEY'),
                   ('longname', 'TEXT'),
                   ('shortname', 'TEXT'),
                   ('machine', 'TEXT'),
                   ('creator', 'TEXT'),
                   ('date', 'REAL'),
                   ('hash', 'TEXT'),
                   ('storage', 'TEXT')]
        createTable("km_sc", columns, self.cursor)
        columns[0] = ('fc_id', 'TEXT PRIMARY KEY')
        columns.insert(7, ('unit', ''))
        createTable("km_fc", columns, self.cursor)
        columns = [('sc_id', 'TEXT'),
                   ('fc_id', 'TEXT'),
                   ('fc_index', 'INT')]
        createTable("km_sc_columns", columns, self.cursor)
        columns = [('fc_id', 'TEXT'),
                   ('dim_id', 'TEXT'),
                   ('dim_index', 'INT')]
        createTable("km_fc_dimensions", columns, self.cursor)
        columns = [('dc_id', 'TEXT'),
                   ('key', 'TEXT'),
                   ('value', 'TEXT')]
        createTable('km_attributes', columns, self.cursor)
        columns = [('dc_id', 'TEXT PRIMARY KEY')]
        createTable("km_temporary", columns, self.cursor)
        #cleanup tmp mess from last time:
        query = "SELECT dc_id FROM km_temporary"
        self.cursor.execute(query)
        ids = self.cursor.fetchall()
        self.cursor.executemany("DELETE FROM km_fc WHERE fc_id=?", ids)
        self.cursor.executemany("DELETE FROM km_sc WHERE sc_id=?", ids)
        self.cursor.executemany("DELETE FROM km_attributes WHERE dc_id=?", ids)
        self.cursor.execute("DELETE FROM km_temporary")

    def has_entry(self, id):
        exe = self.cursor.execute
        type = emd52type(id)
        exe("SELECT %s_id FROM km_%s WHERE %s_id=?" % (type, type, type),
            (id, ))
        return self.cursor.fetchone() != None

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
        insert_dict['date'] = date2dbase(insert_dict['date'])
        insert_dict['storage'] = storage
        type = emd52type(summary['id'])
        attr_query = "INSERT INTO km_attributes VALUES (?, ?, ?)"
        for key, value in summary['attributes'].iteritems():
            assert isinstance(key, StringTypes)
            exe(attr_query, (summary['id'], key, value.__repr__()))
        if type == 'fc':
            insert_dict['fc_id'] = summary['id']
            insert_dict['unit'] = quantity2dbase(summary['unit'])
            dimension_query = "INSERT INTO km_fc_dimensions VALUES (?, ?, ?)"
            for dim_id, dim_index in zip(summary['dimensions'],
                                         range(len(summary['dimensions']))):
                exe(dimension_query, (summary['id'], dim_id, dim_index))
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
            if key == 'date':
                value_query += "julianday(?), "
            else:
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

    def __getitem__(self, key):
        if key == 'unit':
            return dbase2quantity(RowWrapper.__getitem__(self, key))
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
