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

from pyphant.core.RoutingHTTPServer import (RoutingHTTPServer,
                                            UnreachableError)
import sqlite3
from pyphant.core.Helpers import getPyphantPath
from pyphant.core.SQLiteWrapper import create_table
from time import time
from urllib2 import (urlopen, URLError, HTTPError)
from urllib import urlencode
import logging
from pyphant.core.KnowledgeManager import (DCNotFoundError, KnowledgeManager)
from pyphant.core.bottle import (request, send_file)
from json import (dumps, load, loads)
from tempfile import (mkdtemp, mkstemp)
import os
from pyphant.core.WebInterface import WebInterface
from pyphant import __path__ as pyphant_source_path
import pyphant.core.bottle


class SkipError(Exception):
    pass


class RemoteKN(object):
    """
    This class represents a remote KnowledgeNode.
    """

    status_dict = {0:'offline', 1:'online', 2:'disabled'}

    def __init__(self, host, port, status=1, timeout=300.0):
        """
        Arguments:
        - `host`: hostname
        - `port`: port
        - `status`: 0: offline, may get online after timeout
                    1: online, may get offline anytime
                    2: disabled, use enable() to enable
        - `timeout`: refresh interval for status lookup when offline
                     default: 5 min
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
        if not isinstance(other, RemoteKN):
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
        self.uuid = None
        self._status = 2

    def update_status(self):
        if self._status == 2:
            return
        elif self.last_update == None or self._status == 1:
            self.connect()
        else:
            if time() - self.last_update > self.timeout:
                self.connect()

    def connect(self):
        stream = None
        try:
            stream = urlopen(self.url + 'uuid/', timeout=3.0)
            line = stream.readline()
            if line.startswith('urn:uuid:'):
                self._status = 1
                self.uuid = line
            else:
                self._status = 0
                self.logger.error("Remote KM '%s' returned broken uuid: '%s'" \
                                  % (self.url, line))
        except (URLError, IOError, HTTPError):
            self._status = 0
            self.logger.warn("Remote KM '%s' is not responding." % self.url)
        finally:
            if stream != None:
                stream.close()
            self.last_update = time()

    def get_datacontainer_url(self, dc_id, skip):
        self.update_status()
        if self._status == 1:
            if self.uuid in skip:
                raise SkipError()
            else:
                try:
                    query = urlencode({'skip':dumps(skip), 'dc_id':dc_id})
                    url = '%sget_dc_url/?%s' % (self.url, query)
                    stream = urlopen(url, timeout=60.0)
                    assert stream.headers.type == 'application/json'
                    answer = load(stream)
                    stream.close()
                    if answer['dc_url'] == None:
                        raise DCNotFoundError
                    assert len(answer['skip']) >= len(skip)
                    return answer['dc_url'], answer['skip']
                except (URLError, HTTPError, IOError, AssertionError):
                    raise UnreachableError()
        else:
            raise UnreachableError()


class KnowledgeNode(RoutingHTTPServer):
    """
    This class manages communication between one local and arbitrary many
    remote KM instances.
    """

    def __init__(self, local_km=None,
                 host=u'127.0.0.1', port=8080, start=False,
                 web_interface=False, dbase=u'default'):
        """
        Arguments:
        - `local_km`: Local KnowledgeManager instance to hook up to.
          If set to `None`, KnowledgeManager.getInstance() is used.
        - `host`: hostname to listen on
        - `port`: port to listen on
        - `start`: flag that indicates whether to start the server
        - `web_interface`: flag that indicates whether to enable
          the web interface. You can enable/disable it anytime by
          setting (KN instance).web_interface.enabled to `True`/`False`.
        - `dbase`: leave this to 'default', other values are allowed for
                   debug purposes
        """
        RoutingHTTPServer.__init__(self, host, port, start)
        if local_km == None:
            local_km = KnowledgeManager.getInstance()
        self.km = local_km
        self.remotes = []
        if dbase == u'default':
            self._dbase = getPyphantPath('/sqlite3/') + 'kn_remotes.sqlite3'
        else:
            self._dbase = dbase
        self._restore_remotes()
        self._setup_routes()
        self._tempdir = mkdtemp(prefix = 'HDF5Wrap')
        tpl_path = pyphant_source_path[0] + '/templates/'
        if not tpl_path in pyphant.core.bottle.TEMPLATE_PATH:
            pyphant.core.bottle.TEMPLATE_PATH.append(tpl_path)
        self.web_interface = WebInterface(self, web_interface)
        self.km.node = self

    def _restore_remotes(self):
        """
        Loads remotes from dbase.
        """
        connection = sqlite3.connect(self._dbase)
        cursor = connection.cursor()
        try:
            columns = [('host', 'TEXT'), ('port', 'INT'), ('status', 'INT'),
                       ('', 'UNIQUE(host, port)')]
            create_table('kn_remotes', columns, cursor)
            cursor.execute("SELECT * FROM kn_remotes")
            self.remotes = [RemoteKN(host, port, status) \
                            for host, port, status in cursor]
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def _setup_routes(self):
        self.app.add_route('/uuid/', self.get_uuid)
        self.app.add_route('/get_dc_url/', self.handle_datacontainer_url)
        self.app.add_route(r'/wrapped/:filename#..*\.hdf$#',
                           self.handle_wrapped)

    def stop(self):
        RoutingHTTPServer.stop(self)
        if not hasattr(self, '_tempdir'):
            return
        if os.path.isdir(self._tempdir):
            from shutil import rmtree
            try:
                rmtree(self._tempdir)
            except OSError:
                km.logger.warn("Could not delete '%s'." % self._tempdir)

    def register_remote(self, host, port):
        host = host.lower()
        port = int(port)
        connection = sqlite3.connect(self._dbase)
        cursor = connection.cursor()
        try:
            try:
                cursor.execute("INSERT OR ABORT INTO kn_remotes "\
                               "(host, port, status) "\
                               "VALUES (?, ?, ?)", (host, port, 0))
                self.remotes.append(RemoteKN(host, port))
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
        dummy = RemoteKN(host, port, status=2)
        try:
            self.remotes.remove(dummy)
        except ValueError:
            self.km.logger.warn("Remote '%s:%d' is not registered." \
                                % (host, port))
            return
        connection = sqlite3.connect(self._dbase)
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM kn_remotes "\
                           "WHERE host=? AND port=?", (host, port))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def change_remote(self, host, port, status):
        host = host.lower()
        port = int(port)
        dummy = RemoteKN(host, port, status=2)
        for rem in self.remotes:
            if rem == dummy and rem._status != status:
                if status == 2:
                    rem.disable()
                else:
                    rem.enable()
                connection = sqlite3.connect(self._dbase)
                cursor = connection.cursor()
                try:
                    cursor.execute("UPDATE kn_remotes SET status=? "\
                                   "WHERE host=? AND port=?",
                                   (status, host, port))
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()
                return
        self.km.logger.warn("Remote '%s:%d' is not registered." \
                            % (host, port))

    def disable_remote(self, host, port):
        self.change_remote(host, port, 2)

    def enable_remote(self, host, port):
        self.change_remote(host, port, 0)

    def get_uuid(self):
        return self.km.uuid
    uuid = property(get_uuid)

    def get_datacontainer(self, dc_id):
        skip = [self.uuid]
        for remote in self.remotes:
            try:
                dc_url, skip = remote.get_datacontainer_url(dc_id, skip)
                self.km.registerURL(dc_url)
                return self.km.getDataContainer(dc_id)
            except (DCNotFoundError, UnreachableError, SkipError):
                pass
        raise DCNotFoundError()

    def handle_datacontainer_url(self):
        query = request.GET
        skip = loads(query['skip'])
        if self.uuid in skip:
            # This should not happen during normal operation
            self.km.logger.error(
                "KN '%s' has been queried although it is in the skip list.")
        else:
            skip.append(self.uuid)
        dc_id = query['dc_id']
        try:
            dc = self.km.getDataContainer(dc_id, try_remote=False)
            # Wrap data container in temporary HDF5 file
            osFileId, filename = mkstemp(suffix='.hdf',
                                         prefix='dcrequest-',
                                         dir=self._tempdir)
            os.close(osFileId)
            handler = self.km.getH5FileHandler(filename, 'w')
            with handler:
                handler.saveDataContainer(dc)
            dc_url = self.url + "wrapped/" + os.path.basename(filename)
        except DCNotFoundError:
            dc_url = None
            for remote in self.remotes:
                try:
                    dc_url, skip = remote.get_datacontainer_url(dc_id, skip)
                    break
                except (DCNotFoundError, UnreachableError, SkipError):
                    pass
        return {'skip':skip, 'dc_url':dc_url}

    def handle_wrapped(self, filename):
        send_file(filename, self._tempdir,
                  guessmime=False, mimetype='application/x-hdf')


def get_kn_autoport(ports, logger=None, *args, **kargs):
    """
    Returns a KnowledgeNode listening on the first free port in `ports`
    messages are logged to `logger` or stdout if `None`
    If no port is free, a socket.error (no. 98) is raised.
    """
    import socket
    def log(text):
        if logger is None:
            print text
        else:
            logger.warn(text)

    last_error = None
    for port in ports:
        try:
            kn = KnowledgeNode(port=port, *args, **kargs)
            return kn
        except socket.error as err:
            last_error = err
            if err.errno == 98:
                log("Port %d is already in use." % port)
            elif err.errno == 13:
                log("Port %d: Permission denied." % port)
            else:
                raise err
    raise last_error
