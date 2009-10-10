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

"""
This module provides the KnowledgeNode class which is used as an
HTTP communication channel between one local KnowledgeManager and
arbitrary many remote KnowledgeManagers. It comes with a RoutingHTTPServer
and an optional WebInterface.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from pyphant.core.RoutingHTTPServer import RoutingHTTPServer
import sqlite3
from pyphant.core.Helpers import getPyphantPath
from pyphant.core.SQLiteWrapper import create_table
from time import time
from urllib2 import urlopen
import logging


class RemoteKM(object):
    """
    This class represents a remote KnowledgeManager.
    """

    status_dict = {0:'offline', 1:'online', 2:'disabled'}

    def __init__(self, host, port, status=1, timeout=1800.0):
        """
        Arguments:
        - `host`: hostname
        - `port`: port
        - `status`: 0: offline, may get online after timeout
                    1: online, may get offline anytime
                    2: disabled, use enable() to enable
        - `timeout`: refresh interval for status lookup, default: 30 min
        """
        self.host = host
        self.port = port
        self.url = "http://%s:%d/" % (host, port)
        self.timeout = timeout
        self.last_update = None
        self.uuid = None
        self._status = status
        self.logger = logging.getLogger('pyphant')
        self.update_status()

    def __eq__(self, other):
        if not isinstance(other, RemoteKM):
            return False
        else:
            return self.host == other.host and self.port == other.port

    def _get_status(self):
        return self.status_dict[self._status]
    status = property(_get_status)

    def enable(self):
        self._status = 0
        self.update_status()

    def disable(self):
        self.last_update = None
        self._status = 2

    def update_status(self):
        if self._status == 2:
            return
        elif self.last_update == None:
            self.connect()
        else:
            if time() - self.last_update > self.timeout:
                self.connect()

    def connect(self):
        try:
            stream = urllib2.urlopen(self.url + 'uuid/', timeout=10.0)
            line = stream.readline()
            if line.startswith('urn:uuid:'):
                self._status = 1
            else:
                self._status = 0
                self.logger.error("Remote KM '%s' returned broken uuid: '%s'" \
                                  % (self.url, line))
        except (urllib2.URLError, IOError):
            self._status = 0
            self.logger.warn("Remote KM '%s' is not responding." % self.url)
        finally:
            stream.close()
            self.last_update = time()


class KnowledgeNode(RoutingHTTPServer):
    """
    This class manages communication between one local and arbitrary many
    remote KM instances.
    """

    def __init__(self, local_km, host=u'127.0.0.1', port=8080, start=False):
        """
        Arguments:
        - `local_km`: Local KnowledgeManager instance to hook up to.
        - `host`: hostname to listen on
        - `port`: port to listen on
        - `start`: flag that indicates whether to start the server
        """
        RoutingHTTPServer.__init__(self, host, port, start)
        self.km = local_km
        self.remotes = []
        self._dbase = getPyphantPath('/sqlite3/') + 'kn_remotes.sqlite3'
        self._restore_remotes()
        self._setup_routes()

    def _restore_remotes(self):
        """
        Loads remotes from dbase.
        """
        connection = sqlite3.connect(self._dbase)
        cursor = connection.cursor()
        try:
            columns = [('idx', 'INTEGER PRIMARY KEY AUTOINCREMENT '\
                        'NOT NULL UNIQUE'),
                       ('host', 'TEXT'),
                       ('port', 'INT'),
                       ('', 'UNIQUE(host, port)')]
            create_table('kn_remotes', columns, cursor)
            cursor.execute("SELECT * FROM kn_remotes ORDER BY idx ASC")
            self.remotes = [RemoteKM(host, port) for index, host, port \
                            in cursor]
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def _setup_routes(self):
        self.app.add_route('/uuid/', self.get_uuid)

    def register_remote(self, host, port):
        host = host.lower()
        port = int(port)
        connection = sqlite3.connect(self._dbase)
        cursor = connection.cursor()
        try:
            try:
                cursor.execute("INSERT OR ABORT INTO kn_remotes (host, port)"\
                               " VALUES (?, ?)", (host, port))
                self.remotes.append(RemoteKM(host, port))
            except sqlite3.IntegrityError:
                self.km.logger.warn("Remote '%s:%d' already registered." \
                                    % (host, port))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def remove_remote(self, host, port):
        host = host.lower()
        port = int(port)
        dummy = RemoteKM(host, port, connect=False)
        try:
            imax = len(self.remotes)
            for index in xrange(imax):
                self.remotes.remove(dummy)
        except ValueError:
            if index == 0:
                self.km.logger.warn("Remote '%s:%d' is not registered." \
                                    % (host, port))
            else:
                connection = sqlite3.connect(self._dbase)
                cursor = connection.cursor()
                try:
                    cursor.execute("DELETE FROM kn_remotes "\
                                   "WHERE host=? AND port=?", (host, port))
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()

    def get_uuid(self):
        return self.km.uuid
    uuid = property(get_uuid)
