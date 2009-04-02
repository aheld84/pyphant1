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

u"""
knowledge manager

- retrieve data from local HDF5 files for given emd5s
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from pyphant.core.singletonmixin import Singleton
from pyphant.core.DataContainer import parseId
import pyphant.core.PyTablesPersister as ptp

from types import TupleType
import urllib
import cgi

import tempfile

import tables

import os, os.path
import logging
import traceback

import threading
from BaseHTTPServer import HTTPServer #, BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler

WAITING_SECONDS_HTTP_SERVER_STOP = 5

class KnowledgeManagerException(Exception):
    def __init__(self, message, parent_excep=None, *args, **kwds):
        super(KnowledgeManagerException, self).__init__(message, *args, **kwds)
        self._message = message
        self._parent_excep = parent_excep

    #def __repr__(self):
    #    return message+" (reason: %s)" % (str(self._parent_excep),)

class KnowledgeManager(Singleton):

    def __init__(self):
        super(KnowledgeManager, self).__init__()
        self._logger = logging.getLogger("pyphant")
        self._refs = {}
        self._remoteKMs = []
        self._server = None
        #start http server TODO


    def _getServerURL(self):
        if self._server is None:
            return None
        return "http://%s:%d" % (self._http_host, self._http_port)

    def startServer(self, host, port):
        """Start HTTP server.

          host -- full qualified domain name or IP address under which
                  server can be contacted via HTTP
          port -- port of HTTP server

          The data may be announced to other KnowledgeManagers.
        """
        self._http_host = host
        self._http_port = port
        self._http_dir = tempfile.mkdtemp(prefix='pyphant-knowledgemanager')
        self._server = _HTTPServer((host,port),_HTTPRequestHandler)

        class _HTTPServerThread(threading.Thread):
            def run(other):
                self._server.start()
        self._http_server_thread = _HTTPServerThread()
        self._http_server_thread.start()
        self._logger.debug("Started HTTP server."\
                         +" host: %s, port: %d,"\
                         +" temp dir: %s", host, port, self._http_dir)


    def stopServer(self):

        logger = self._logger
        if self.isServerRunning():
            self._server.stop_server = True
            # do fake request
            try:
                urllib.urlopen(self._getServerURL())
            except:
                logger.warn("Fake HTTP request failed when "+\
                                "stopping HTTP server.")
            logger.info("Waiting for HTTP server thread to die...")
            self._http_server_thread.join(WAITING_SECONDS_HTTP_SERVER_STOP)
            if self._http_server_thread.isAlive():
                logger.warn("HTTP server thread could not be stopped.")
            else:
                logger.info("HTTP server has been stopped.")
            self._server = None
            self._http_host = None
            self._http_port = None
            try:
                logger.debug("Deleting temporary directory '%s'..", self._http_dir)
                os.removedirs(self._http_dir)
            except Exception, e:
                logger.warn("Failed to delete temporary directory '%s'.", self._http_dir)
            self._http_dir = None
        else:
            self._logger.warn("HTTP server should be stopped but isn't running.")

    def isServerRunning(self):
        return self._server is not None

    def registerKnowledgeManager(self, url):
        if url not in self._remoteKMs:
            self._remoteKMs.append(url)

    def registerURL(self, url):
        self._retrieveURL(url)

    def registerDataContainer(self, datacontainer):
        try:
            assert datacontainer.id is not None
            self._refs[datacontainer.id] = datacontainer
        except Exception, e:
            raise KnowledgeManagerException("Invalid id for DataContainer '" +\
                                                datacontainer.longname+"'", e)


    def _retrieveURL(self, url):

        self._logger.info("Retrieving url '%s'..." % (url,))
        localfilename, headers = urllib.urlretrieve(url)
        self._logger.info("Using local file '%s'." % (localfilename,))
        self._logger.info("Header information: %s", (str(headers),))

        #
        # Save index entries
        #
        h5 = tables.openFile(localfilename)
        # title of 'result_' groups has id in TITLE attribute
        dc = None
        for group in h5.walkGroups(where="/results"):
            id = group._v_attrs.TITLE
            if len(id)>0:
                self._logger.debug("Registering id '%s'.." % (id,))
                self._refs[id] = (url, localfilename, group._v_pathname)

        h5.close()

    def _retrieveRemoteKMs(self, id, omit_km_urls):
        id_url = self._getURLFromRemoteKMs(id, omit_km_urls)
        if id_url is None:
            raise KnowledgeManagerException(
                "Couldn't retrieve ID '%s' from remote knowledgemanagers" % (id,))
        else:
            self._retrieveURL(id_url)

    def _getURLFromRemoteKMs(self, id, omit_km_urls):

        logger = self._logger
        #
        # build query for http request with
        # id of data container and
        # list of URLs which should not be requested by
        # the remote side
        #
        query = { 'id': id}
        for idx,km_url in enumerate(omit_km_urls):
            query['url%d' % (idx,)] = km_url

        serverURL = self._getServerURL()
        if serverURL is not None:
            idx += 1
            query['url%d' % (idx,)] = serverURL

        #
        # ask every remote KnowledgeManager for id
        #
        logger.debug("Requesting knowledge managers for id '%s'..." % (id,))
        found = False
        id_url = None
        for km_url in self._remoteKMs:
            if not (found or (km_url in omit_km_urls)):
                logger.debug("Requesting Knowledgemanager with URL '%s'...", km_url)
                # request url for given id over http
                data = urllib.urlencode(query)
                logger.debug("URL encoded query: %s", data)
                answer = urllib.urlopen(km_url, data)
                logger.debug("Info from HTTP answer: %s", answer.info())
                id_url = answer.readline()
                logger.debug("URL for id read from HTTP answer: %s", id_url)
                found = True # TODO not 404?
                if not found:
                    # message for everyone: do not ask this KM again
                    idx += 1
                    query['url%d' % (idx),] = km_url
        return id_url


    def getDataContainerURL(self, id, omit_km_urls=[]):

        if id in self._refs.keys():
            dc = self.getDataContainer(id, omit_km_urls=omit_km_urls)

            #
            # Wrap data container in temporary HDF5 file
            #
            h5fileid, h5name = tempfile.mkstemp(suffix='.h5',
                                                prefix='dcrequest-',
                                                dir=self._http_dir)
            os.close(h5fileid)

            h5 = tables.openFile(h5name,'w')
            resultsGroup = h5.createGroup("/", "results")
            ptp.saveResult(dc, h5)
            h5.close()
            url = self._getServerURL()+"/"+os.path.basename(h5name)
        else:
            try:
                url = self._getURLFromRemoteKMs(id, omit_km_urls)
            except Exception, e:
                raise KnowledgeManagerException(
                    "URL for ID '%s' not found." % (id,))
        return url

    def getDataContainer(self, id, try_cache=True, omit_km_urls=[]):
        if id not in self._refs.keys():
            # raise KnowledgeManagerException("Id '%s'unknown."%(id,))
            try:
                self._retrieveRemoteKMs(id, omit_km_urls)
            except Exception, e:
                raise KnowledgeManagerException("Id '%s' unknown." % (id,))

        ref = self._refs[id]
        if isinstance(ref, TupleType):
            dc = self._getDCfromURLRef(id, try_cache = try_cache)
        else:
            dc = ref

        return dc

    def _getDCfromURLRef(self, id, try_cache=True, omit_km_urls=[]):
        url, localfilename, h5path = self._refs[id]
        if not try_cache:
            os.remove(localfilename)

        if not os.path.exists(localfilename):
            try:
                # download URL and save ids as references
                self._retrieveURL(url)
            except Exception, e_url:
                try:
                    self._retrieveRemoteKMs(id, omit_km_urls)
                except Exception, e_rem:
                    raise KnowledgeManagerException(
                        "Id '%s' not found on remote sites."%(id,),
                        KnowledgeManagerException(
                            "Id '%s' could not be resolved using URL '%s'"%(id, url)))

            url, localfilename, h5path = self._refs[id]

        h5 = tables.openFile(localfilename)

        hash, type = parseId(id)
        assert type in ['sample','field']
        if type=='sample':
            loader = ptp.loadSample
        elif type=='field':
            loader = ptp.loadField
        else:
            raise KnowledgeManagerException("Unknown result type '%s'" \
                                                % (type,))
        try:
            self._logger.debug("Loading data from '%s' in file '%s'.." % (localfilename, h5path))
            dc = loader(h5, h5.getNode(h5path))
        except Exception, e:
            raise KnowledgeManagerException("Id '%s' known, but cannot be read from file '%s'." \
                                                % (id,localfilename), e)
        finally:
            h5.close()
        return dc

class _HTTPRequestHandler(SimpleHTTPRequestHandler):

    _knowledge_manager = KnowledgeManager.getInstance()
    _logger = logging.getLogger("pyphant")

    def do_POST(self):
        self._logger.debug("POST request from client (host,port): %s",
                           self.client_address)
        self.log_request()

        if self.headers.has_key('content-length'):
            length= int( self.headers['content-length'] )
            query = self.rfile.read(length)
            query_dict = cgi.parse_qs(query)

            id = query_dict['id'][0]
            omit_km_urls = [ value[0] for (key,value) in query_dict.iteritems()
                             if key!='id']
            self._logger.debug("Query data: id: %s, omit_km_urls: %s",
                               id, omit_km_urls)

            try:
                km = _HTTPRequestHandler._knowledge_manager
                code = 200
                answer = km.getDataContainerURL(id, omit_km_urls)
                self._logger.debug("Returning URL '%s'...", answer)
            except Exception, e:
                self._logger.warn("Catched exception: %s", traceback.format_exc())
                code = 404
                answer = "Id '%s' not found." % (id,)
        else:
            code = 404
            answer = "Cannot interpret query."

        self.send_response(code)
        self.end_headers()
        self.wfile.write(answer)
        self.wfile.write('\n')


    def do_GET(self):
        """Serve a GET request."""
        log = self._logger
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
            try:
                log.debug("Trying to remove temporary file '%s'..", f.name)
                os.remove(f.name)
            except Exception, e:
                log.warn("Cannot delete temporary file '%s'.", f.name)



    def send_head(self): # see SimpleHTTPServer.SimpleHTTPRequestHandler

        log = self._logger

        km = _HTTPRequestHandler._knowledge_manager
        source_dir = km._http_dir # this is intended
        log.debug("HTTP GET request: "\
                      +"Reading files from directory '%s'..", source_dir)

        try:
            # build filename, remove preceding '/' in path
            filename = os.path.join(source_dir, self.path[1:])
            log.debug("Returning file '%s' as answer for HTTP request..",
                      filename)
            f = open(filename, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", "application/x-hdf")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f


class _HTTPServer(HTTPServer):

    stop_server = False
    _logger = logging.getLogger("pyphant")

    def start(self):
        while not self.stop_server:
            self.handle_request()
        self._logger.info("Stopped HTTP server.")




