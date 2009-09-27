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


class SQLiteWrapper(object):
    """Wrapper class for KM summary dict <-> SQLite3
    """
    common_keys = ['id', 'longname', 'shortname', 'type', 'date', 'creator',
                   'machine', 'filename', 'hash']
    
    def __init__(self, database=':memory:'):
        """
        
        Arguments:
        - `database`: database to connect to
        """
        self.database = database
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        assert self.connection == None
        assert self.cursor == None
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        if type == None:
            try:
                self.cursor.commit()
            except:
                print "Could not commit changes to database."
        if hasattr(self.cursor, 'close'):
            self.cursor.close()
        if hasattr(self.connection, 'close'):
            self.connection.close()
        self.cursor = None
        self.connection = None
        
    def __getitem__(self, emd5):
        return RowWrapper(emd5, self.cursor)

    def set_summary(self, summary):
        """Updates the meta data in the database according to the
        summary dictionary.
        
        Arguments:
        - `self`:
        - `summary`: dictionary with meta data
        """
        pass


class RowWrapper(object):
    
    def __init__(self, emd5, cursor):
        self.cursor = cursor
        self.emd5 = emd5

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass
