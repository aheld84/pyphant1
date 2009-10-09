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
from __future__ import with_statement

"""
This module provides the KnowledgeManager class as well as some helper methods
for handling the .pyphant directory and some helper classes for the
KnowledgeManager class.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from pyphant.core.singletonmixin import Singleton
import urllib
import cgi
import tempfile
import sys
import os, os.path
import logging
import threading
from uuid import uuid1
import re
import time
from urlparse import urlparse
from SimpleHTTPServer import SimpleHTTPRequestHandler
from pyphant.core.H5FileHandler import H5FileHandler
from pyphant.core.WebInterface import (HTTPAnswer,
                                       WebInterface,
                                       KMHTMLParser,
                                       ThreadedHTTPServer)
from fmfile import FMFLoader
from pyphant.core.SQLiteWrapper import (SQLiteWrapper, AnyValue)

WAITING_SECONDS_HTTP_SERVER_STOP = 5
HTTP_REQUEST_DC_URL_PATH = "/request_dc_url"
HTTP_REQUEST_KM_ID_PATH = "/request_km_id"
HTTP_REQUEST_DC_DETAILS_PATH = "/request_dc_details?dcid="
HTTP_REQUEST_REGISTER_KM = "/request_register_km"
HTTP_REQUEST_SEARCH = "/request_search"
# Limit for sum(DC.rawDataBytes) for DC in cache:
CACHE_MAX_SIZE = 256 * 1024 * 1024
# Limit for number of stored DCs in cache:
CACHE_MAX_NUMBER = 100
KM_PATH = '/KMstorage/'
REHDF5 = re.compile(r'..*\.h5$|..*\.hdf$|..*\.hdf5$')
REFMF = re.compile(r'..*\.fmf$')

def getPyphantPath(subdir = '/'):
    """
    returns full pyphant path with optional subdirectory
    subdir -- subdirectory that is created if it does not exist already,
              recursive creation of directories is supported also.
    """
    homedir = os.path.expanduser('~')
    if not subdir.startswith('/'):
        subdir = '/' + subdir
    if not subdir.endswith('/'):
        subdir = subdir + '/'
    if homedir == '~':
        homedir = os.getcwdu()
    plist = ('/.pyphant' + subdir).split('/')
    makedir = homedir
    path = homedir + '/.pyphant' + subdir
    for p in plist:
        if p != '':
            makedir += "/%s" % (p, )
            if not os.path.isdir(makedir):
                os.mkdir(makedir)
    return path

def getFilenameFromDcId(dcId, temporary=False):
    """
    Returns a unique filename for the given emd5.
    """
    emd5list = urlparse(dcId + '.h5')[2][2:].split('/')
    emd5path = ''
    for p in emd5list[:-2]:
        emd5path += (p + '/')
    emd5path += emd5list[-2][:10] + '/' + emd5list[-2][11:]\
        + '.' + emd5list[-1]
    directory = os.path.dirname(emd5path)
    filename = os.path.basename(emd5path)
    if temporary:
        subdir = 'tmp/by_emd5/'
    else:
        subdir = 'by_emd5/'
    return getPyphantPath(KM_PATH + subdir + directory) + filename


class KnowledgeManagerException(Exception):
    """
    Exception class that is able to store parent exceptions.
    """
    def __init__(self, message, parent_excep = None, *args, **kwds):
        """
        message -- human readable reason for the exception
        parent_excep -- exception that is the reason for throwing this one.
        """
        super(KnowledgeManagerException, self).__init__(message, *args, **kwds)
        self._message = message
        self._parent_excep = parent_excep

    def __str__(self):
        """
        Returns error message with reason from parent exception.
        """
        return self._message + " (reason: %s)" % (str(self._parent_excep), )

    def getParentException(self):
        """
        Returns the parent exception
        """
        return self._parent_excep


class CachedDC(object):
    def __init__(self, dc_ref):
        self.id = dc_ref.id
        self.ref = dc_ref
        self.size = dc_ref.rawDataBytes

    def __eq__(self, other):
        return self.id == other.id


class TestCachedDC(object):
    def __init__(self, dc_id):
        self.id = dc_id

    def __eq__(self, other):
        return self.id == other.id


class KnowledgeManager(Singleton):
    """
    Knowledge Manager for Pyphant
    =============================
    The ID of a DataContainer object is given by a emd5 string.
    Responsibilities:
    -----------------
    - register HDF5 files by their URLs
    - register remote knowledge managers by urls
    - share data containers via HTTP, they are requested by id
    - get references for these data containers (local or remote)
    If an operation fails, a KnowledgeManagerException
    will be raised. These exceptions have a method
    .getParentException()
    in order to get additional information about the reason.
    Usage:
    ------
    Get a reference to the KnowledgeManager instance, which is a
    singleton:
    import pyphant.core.KnowledgeManager as KM
        km = KM.KnowledgeManager.getInstance()
    Optionally: Start HTTP server for sharing data with others by
        km.startServer(<host>,<port>)
    Register a local HDF5 file:
        km.registerURL("file:///tmp/data.h5")
    Register a remote HDF5 file:
        km.registerURL("http://example.com/repository/data.h5")
    Register another KnowledgeManager in order to benefit
    from their knowledge (see arguments of .startServer):
        km.registerKnowledgeManager("http://example.com", 8000, True)
    Request data container by its id:
        dc = km.getDataContainer(id)
    Use the data container!
    """
    def __init__(self):
        """
        Sets the unique id for the KM instance, sets up the DataBase if
        it has not been initialized yet and clears the tmp dir.
        """
        super(KnowledgeManager, self).__init__()
        self._logger = logging.getLogger("pyphant")
        self._cache = []
        self._cache_size = 0
        self.H5FileHandlers = {}
        self._remoteKMs = {} # key:id, value:url
        self._server = None
        self._server_id = uuid1()
        self.web_interface = WebInterface(self, True)
        self.dbase = getPyphantPath('/sqlite3/') + "km_meta.sqlite3"
        self.any_value = AnyValue()
        with SQLiteWrapper(self.dbase) as wrapper:
            wrapper.setup_dbase()
        tmpdir = getPyphantPath(KM_PATH + 'tmp/')
        if os.path.isdir(tmpdir):
            from shutil import rmtree
            try:
                rmtree(tmpdir)
            except OSError:
                print "Could not delete '%s'." % (tmpdir, )

    def tearDown(self):
        """
        Stops the HTTP server
        """
        if self.isServerRunning():
            self.stopServer()

    def hasDataContainer(self, dcid):
        """
        Returns whether the given DC is stored locally.
        Never use this method in a 'with SQLiteWrapper(...) as wrapper'
        statement! Use wrapper.has_entry(dcid) instead if you already
        have a wrapper at your hands or you may end up in a sqlite3 locking
        loop.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            has_entry = wrapper.has_entry(dcid)
        return has_entry

    def getH5FileHandler(self, filename, mode='r'):
        """
        Returns an H5FileHandler for the given filename to perform IO
        operations on the file in a save way.
        filename -- path to the HDF5 file
        mode -- see H5FileHandler
        """
        return H5FileHandler(filename, mode)

    def registerH5(self, filename, temporary=False):
        """
        Adds the given file to the knowledge pool. If you want the data to
        be copied to the .pyphant directory, use registerURL() instead.
        filename -- path to the HDF5 file
        temporary -- flag that marks data to be deleted upon next
                     instantiation of a KM Singleton
        """
        h5fh = self.getH5FileHandler(filename)
        with h5fh:
            summaryDict = h5fh.loadSummary()
        with SQLiteWrapper(self.dbase) as wrapper:
            for dcId, summary in summaryDict.items():
                if not wrapper.has_entry(dcId):
                    wrapper.set_entry(summary, filename, temporary)

    def _getServerURL(self):
        """
        Returns the URL of the HTTP server.
        """
        if self._server is None:
            return None
        return "http://%s:%d" % (self._http_host, self._http_port)

    def getServerId(self):
        """
        Returns uniqe id of the KnowledgeManager as uuid URN.
        """
        return self._server_id.urn

    def startServer(self, host = '127.0.0.1', port = 8000,
                    provide_web_frontend = False):
        """
        Starts the HTTP server. When the server was running already,
        it is restartet with the new parameters.
        A temporary directory is generated in order to
        save temporary HDF5 files.
        The data may be announced to other KnowledgeManagers.
        host -- full qualified domain name or IP address under which
                server can be contacted via HTTP, default: '127.0.0.1'
        port -- port of HTTP server (integer), default: 8000
        provide_web_frontend -- whether to provide web frontend, default: False
        """
        logger = self._logger
        if self.isServerRunning():
            logger.warn("Server is running at host %s, port %d already. "
                        "Stopping server...", self._http_host, self._http_port)
            self.stopServer()
        self._http_host = host
        self._http_port = port
        self._http_dir = tempfile.mkdtemp(prefix = 'pyphant-knowledgemanager')
        self._server = ThreadedHTTPServer((host, port), KMHTTPRequestHandler)
        class _HTTPServerThread(threading.Thread):
            def run(other):
                self._server.start()
        self._http_server_thread = _HTTPServerThread()
        self._http_server_thread.start()
        self._logger.debug("Started HTTP server. Host: %s, port: %d, "
                           "temp dir: %s", host, port, self._http_dir)
        self.web_interface.disabled = not provide_web_frontend

    def stopServer(self):
        """
        Stops the HTTP server. The temporary directory is removed.
        """
        logger = self._logger
        if self.isServerRunning():
            self.web_interface.disabled = True
            self._server.stop_server = True
            # do fake request
            try:
                urllib.urlopen(self._getServerURL())
            except:
                logger.warn("Fake HTTP request failed when stopping HTTP "
                            "server.")
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
                logger.debug("Deleting temporary directory '%s'..",
                             self._http_dir)
                os.removedirs(self._http_dir)
            except Exception:
                logger.warn("Failed to delete temporary directory '%s'.",
                            self._http_dir)
            self._http_dir = None
        else:
            self._logger.warn("HTTP server should be stopped but isn't "
                              "running.")

    def isServerRunning(self):
        """
        Returns whether HTTP server is running.
        """
        return self._server is not None

    def registerKnowledgeManager(self, host, port = 8000,
                                 share_knowledge = False):
        """
        Registers a knowledge manager. The remote KnowledgeManager is
        contacted immediately in order to save its unique ID.
        host -- full qualified domain name or IP address at which
                server can be contacted via HTTP
        port -- port of HTTP server (integer), default: 8000
        share_knowledge -- local knowledge is made available to the remote KM
                           when set to True and the HTTP server is running at
                           the local KM, default: False
        """
        logger = self._logger
        try:
            km_url = "http://%s:%d" % (host, port)
            # get unique id from KM via HTTP
            logger.debug("Requesting ID from Knowledgemanager with URL '%s'...",
                         km_url)
            # request url for given id over http
            local_km_host = ''
            local_km_port = ''
            if self.isServerRunning() and share_knowledge:
                local_km_host = self._http_host
                local_km_port = str(self._http_port)
            post_data = urllib.urlencode({'kmhost':local_km_host,
                                          'kmport':local_km_port})
            answer = urllib.urlopen(km_url + HTTP_REQUEST_KM_ID_PATH, post_data)
            logger.debug("Info from HTTP answer: %s", answer.info())
            htmltext = answer.read()
            parser = KMHTMLParser()
            parser.feed(htmltext)
            km_id = parser.headitems['pyphant']['kmid'].strip()
            answer.close()
            logger.debug("KM ID read from HTTP answer: %s", km_id)
        except Exception, excep:
            raise KnowledgeManagerException(
                "Couldn't get ID for knowledge manager under URL %s."
                % (km_url, ), excep)
        self._remoteKMs[km_id] = km_url

    def registerURL(self, url, temporary=False):
        """
        Registers an HDF5 or FMF file downloadable from given URL and stores it
        in the .pyphant directory. The content of the file is made
        available to the KnowledgeManager.
        HTTP redirects are resolved. The filetype is determined by the
        extension.
        url -- URL of the HDF5 or FMF file
        temporary -- set to True in order to mark the data to be deleted upon
                     next instantiation of a KM singleton
        """
        parsed = urlparse(url)
        tmp_extension = ''
        if temporary:
            tmp_extension = 'tmp/'
        filename = KM_PATH + tmp_extension + 'registered/' + parsed[1] + '/'
        filename += os.path.basename(parsed[2])
        directory = os.path.dirname(filename)
        filename = getPyphantPath(directory) + os.path.basename(filename)
        if os.path.exists(filename):
            i = 0
            directory = os.path.dirname(filename)
            basename = os.path.basename(filename)
            split = basename.split('.')
            ext = split.pop()
            fnwoext = ''
            for part in split:
                fnwoext += (part + '.')
            while i < sys.maxint:
                fill = str(i).zfill(10)
                tryfn = "%s/%s%s.%s" % (directory, fnwoext, fill, ext)
                if os.path.exists(tryfn):
                    i += 1
                else:
                    filename = tryfn
                    break
        self._logger.info("Retrieving url '%s'..." % (url, ))
        self._logger.info("Using local file '%s'." % (filename, ))
        savedto, headers = urllib.urlretrieve(url, filename)
        self._logger.info("Header information: %s", (str(headers), ))
        if REFMF.match(filename.lower()) != None:
            self.registerFMF(filename, temporary)
        elif REHDF5.match(filename.lower()) != None:
            self.registerH5(filename, temporary)
        else:
            raise KnowledgeManagerException('Filetype unknown: %s'
                                            % (filename, ))

    def registerDataContainer(self, dc, temporary=False):
        """
        Registers a DataContainer located in memory using a given
        reference and stores it in the pyphant directory.
        The DataContainer must have an .id attribute,
        which could be generated by the datacontainer.seal() method.
        If the DCs emd5 is already known to the KnowledgeManager,
        the DC is not registered again since emd5s are unique.
        dc -- reference to the DataContainer object
        temporary -- dc is stored only until another KM singleton is
                     created. Set this flag to True e.g. for unit tests
                     or whenever you do not want to produce garbage on
                     your hard drive.
        """
        if dc.id == None:
            raise KnowledgeManagerException("Invalid id for DataContainer '"\
                                            + dc.longname + "'")
        if not self.hasDataContainer(dc.id):
            filename = getFilenameFromDcId(dc.id, temporary)
            handler = self.getH5FileHandler(filename, 'w')
            with handler:
                handler.saveDataContainer(dc)
            self.registerH5(filename, temporary)

    def registerFMF(self, filename, temporary=False):
        """
        Extracts a SampleContainer from a given FMF file and stores it
        permanently. The emd5 of the SampleContainer that has been generated
        is returned.
        filename -- path to the FMF file
        temporary -- see registerDataContainer
        """
        sc = FMFLoader.loadFMFFromFile(filename)
        self.registerDataContainer(sc, temporary)
        return sc.id

    def _getDCURLFromRemoteKMs(self, query_dict):
        """
        Returns URL for a DataContainer by requesting remote
        KnowledgeManagers.
        query_dict -- see _getDataContainerURL
        """
        logger = self._logger
        # add this KM to query
        query_dict['lastkmidindex'] += 1
        query_dict['kmid%d' % query_dict['lastkmidindex']] = self.getServerId()
        # ask every remote KnowledgeManager for id
        logger.debug("Requesting knowledge managers for DC id '%s'..."
                     % (query_dict['dcid'], ))
        dc_url = None
        for km_id, km_url in self._remoteKMs.iteritems():
            if not (km_id in query_dict.values()): #<-- TODO: exclude wrong keys
                logger.debug("Requesting Knowledgemanager with ID '%s' and \
URL '%s'...", km_id, km_url)
                # request url for given id over http
                try:
                    data = urllib.urlencode(query_dict)
                    logger.debug("URL encoded query: %s", data)
                    answer = urllib.urlopen(km_url + HTTP_REQUEST_DC_URL_PATH,
                                            data)
                    code = int(answer.headers.dict['code'])
                    if code < 400:
                        parser = KMHTMLParser()
                        htmltext = answer.read()
                        parser.feed(htmltext)
                        dc_url = parser.headitems['pyphant']['hdf5url'].strip()
                        logger.debug("URL for id read from HTTP answer: %s",
                                     dc_url)
                        break
                    elif code == 404:
                        # update query_dict:
                        parser = KMHTMLParser()
                        htmltext = answer.read()
                        parser.feed(htmltext)
                        query_dict.clear()
                        for k in parser.headitems['pyphant']:
                            query_dict[k] =\
                                parser.headitems['pyphant'][k].strip()
                        query_dict['lastkmidindex']\
                            = int(query_dict['lastkmidindex'])
                        logger.debug("Code 404 from '%s', updated query: %s",
                                     km_url, str(query_dict))
                    else:
                        # message for everyone: do not ask this KM again
                        query_dict['lastkmidindex'] += 1
                        query_dict['kmid%d' % (query_dict['lastkmidindex'], )]\
                            = km_id
                except:
                    logger.debug("Could not contact KM with ID '%s'", km_id)
                    # message for everyone: do not ask this KM again
                    query_dict['lastkmidindex'] += 1
                    query_dict['kmid%d' % (query_dict['lastkmidindex'], )]\
                        = km_id
                finally:
                    answer.close()
        return dc_url

    def _getDataContainerURL(self, query_dict):
        """
        Returns a URL from which a DataContainer can be downloaded.
        The server must be running before calling this method.
        query_dict -- dict of DC ID to get and KnowledgeManager IDs
                      which shouldn't be asked.
                      e.g.: {'dcid':'somedcid',
                             'lastkmidindex:1',
                             'kmid0':'someid',
                             'kmid1':'anotherid'}
                      query_dict is extended by this method in order to
                      exclude KMs recursively.
        """
        assert self.isServerRunning(), "Server is not running."
        dc_id = query_dict['dcid']
        if self.hasDataContainer(dc_id):
            dc = self.getDataContainer(dc_id, True, False)
            # Wrap data container in temporary HDF5 file
            osFileId, filename = tempfile.mkstemp(suffix = '.h5',
                                                  prefix = 'dcrequest-',
                                                  dir = self._http_dir)
            os.close(osFileId)
            handler = H5FileHandler(filename, 'w')
            with handler:
                handler.saveDataContainer(dc)
            dc_url = self._getServerURL() + "/" + os.path.basename(filename)
        else:
            try:
                dc_url = self._getDCURLFromRemoteKMs(query_dict)
            except Exception, excep:
                raise KnowledgeManagerException(
                    "URL for DC ID '%s' not found." % (dc_id, ), excep)
        return dc_url

    def getDCFromCache(self, dc_id, filename):
        """
        Returns a DC instance from cache or local storage.
        Also puts DC to cache if reasonable.
        fc_id: emd5 to look for in cache
        filename: alternative source if dc_id not present in cache
        """
        try:
            index = self._cache.index(TestCachedDC(dc_id))
            cached = self._cache.pop(index)
            self._cache.append(cached)
            return cached.ref
        except ValueError:
            with self.getH5FileHandler(filename) as handler:
                dc = handler.loadDataContainer(dc_id)
            self._attemptToCacheDC(dc)
            return dc

    def _attemptToCacheDC(self, dc):
        cache_item = CachedDC(dc)
        if cache_item.size > CACHE_MAX_SIZE:
            return
        number_fits = len(self._cache) < CACHE_MAX_NUMBER
        self._cache.reverse()
        if not number_fits:
            self._cache_size -= self._cache.pop().size
        desired_size = CACHE_MAX_SIZE - cache_item.size
        not_size_fits = self._cache_size > desired_size
        while not_size_fits:
            self._cache_size -= self._cache.pop().size
            not_size_fits = self._cache_size > desired_size
        self._cache.reverse()
        self._cache.append(cache_item)
        self._cache_size += cache_item.size

    def getDataContainer(self, dc_id, use_cache = True, try_remote = True):
        """
        Returns DataContainer matching the given id.
        dc_id -- Unique ID of the DataContainer (emd5)
        use_cache -- Try local cache first and cache DC for further
                     lookups (default: True)
        try_remote -- Try to get DC from remote KMs (default: True)
        """
        filename = None
        with SQLiteWrapper(self.dbase) as wrapper:
            try:
                filename = wrapper[dc_id]['storage']
            except KeyError:
                pass
        if filename != None:
            if use_cache:
                return self.getDCFromCache(dc_id, filename)
            with self.getH5FileHandler(filename) as handler:
                dc = handler.loadDataContainer(dc_id)
            return dc
        elif try_remote:
            dc_url = self._getDCURLFromRemoteKMs({'dcid':dc_id,
                                                  'lastkmidindex':-1})
            if dc_url == None:
                raise KnowledgeManagerException("DC ID '%s' is unknown."
                                                % (dc_id,))
            filename = getFilenameFromDcId(dc_id)
            urllib.urlretrieve(dc_url, filename)
            self.registerH5(filename)
            with self.getH5FileHandler(filename) as handler:
                dc = handler.loadDataContainer(dc_id)
            return dc
        else:
            raise KnowledgeManagerException("DC ID '%s' is unknown."
                                            % (dc_id, ))

    def getEmd5List(self):
        """
        returns a list with all locally known DataContainer ids.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            return wrapper.get_emd5_list()

    def search(self, result_keys, search_dict={}, order_by=None,
               order_asc=True, limit=-1, offset=0, distinct=False):
        """
        See SQLiteWrapper.get_andsearch_result()
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            return wrapper.get_andsearch_result(
                result_keys, search_dict, order_by, order_asc,
                limit, offset, distinct)

    def getSummary(self, dc_id):
        """
        This method returns a dictionary with meta information about
        the given DC.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            # TODO: usage of rowwrapper is not optimal in performance
            rowwrapper = wrapper[dc_id]
            keys = list(SQLiteWrapper.all_keys)
            if dc_id.endswith('field'):
                keys.remove('columns')
            elif dc_id.endswith('sample'):
                keys.remove('unit')
                keys.remove('dimensions')
            summary = dict([(key, rowwrapper[key]) for key in keys])
        return summary


class KMHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    Helper class for KnowledgeManager that handles HTTP requests.
    """
    _km = KnowledgeManager.getInstance()
    _logger = logging.getLogger("pyphant")
    def send_response(self, code, message = None):
        """
        Sends HTTP status code and an optional message via HTTP headers.
        code -- HTTP status code e.g. 404: File not found
        message -- optional reason for the given code
        """
        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s %d %s\r\n" % (self.protocol_version, code,
                                               message))
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        #for older versions of urllib.urlopen which do not support
        #.getcode() method
        self.send_header('code', str(code))

    def do_POST(self):
        """
        Handles HTTP POST requests.
        """
        self._logger.debug("POST request from client (host,port): %s",
                           self.client_address)
        self._logger.debug("POST request path: %s", self.path)
        if self.path == HTTP_REQUEST_DC_URL_PATH:
            httpanswer = self._do_POST_request_dc_url()
        elif self.path == HTTP_REQUEST_KM_ID_PATH:
            httpanswer = self._do_POST_request_km_id()
        elif self.path == HTTP_REQUEST_REGISTER_KM:
            httpanswer = self._do_POST_request_register_km()
        else:
            code = 400
            message = "Unknown request path '%s'." % (self.path, )
            httpanswer = HTTPAnswer(code, message)
        httpanswer.sendTo(self)

    def _do_POST_request_km_id(self):
        """
        Returns the KnowledgeManager ID via HTTP in the HTML head as
        "<pyphant kmid = '...'>".
        """
        km = KMHTTPRequestHandler._km
        if self.headers.has_key('content-length'):
            length = int( self.headers['content-length'] )
            query = self.rfile.read(length)
            query_dict = cgi.parse_qs(query)
            remote_host = ''
            remote_port = ''
            try:
                remote_host = query_dict['kmhost'][0]
                remote_port = query_dict['kmport'][0]
            except:
                #self._logger.info("Remote knowledge is not being shared.")
                pass
            if remote_host != '' and remote_port != '':
                km.registerKnowledgeManager(remote_host, int(remote_port),
                                            False)
        self._logger.debug("Returning ID '%s'...", km.getServerId())
        return km.web_interface.get_kmid(km.getServerId())

    def _do_POST_request_dc_url(self):
        """
        Returns an URL for a given DataContainer ID via HTTP in the HTML head as
        "<pyphant hdf5url = '...'>".
        """
        if self.headers.has_key('content-length'):
            length = int( self.headers['content-length'] )
            query = self.rfile.read(length)
            tmp_dict = cgi.parse_qs(query)
            query_dict = dict([(k, v[0]) for (k, v) in tmp_dict.items()\
                               if (k.startswith('kmid')\
                               or k == 'lastkmidindex' or k =='dcid')])
            query_dict['lastkmidindex'] = int(query_dict['lastkmidindex'])
            self._logger.debug("Query dict: %s", str(query_dict))
            try:
                km = KMHTTPRequestHandler._km
                redirect_url = km._getDataContainerURL(query_dict)
                if redirect_url != None:
                    self._logger.debug("Returning URL '%s'...", redirect_url)
                    httpanswer = km.web_interface.get_kmurl(redirect_url,
                                                            query_dict['dcid'])
                else:
                    self._logger.debug("Returning Error Code 404: \
DataContainer ID '%s' not found.", query_dict['dcid'])
                    httpanswer = km.web_interface.get_updatequery(query_dict)
            except Exception, excep:
                self._logger.warn("Caught exception: %s", excep.message)
                httpanswer = km.web_interface.get_internalerror(excep)
        else:
            httpanswer = HTTPAnswer(400, "Cannot interpret query.")
        return httpanswer

    def _do_POST_request_register_km(self):
        length = int( self.headers['content-length'] )
        query = self.rfile.read(length)
        dict = cgi.parse_qs(query)
        km = KMHTTPRequestHandler._km
        host = dict['remote_km_host'][0]
        port = int(dict['remote_km_port'][0])
        try:
            km.registerKnowledgeManager(host, port, False)
        except KnowledgeManagerException:
            emsg = "Host '%s:%d' is not a KnowledgeManager."
            return HTTPAnswer(400, emsg % (host, port))
        return km.web_interface.get_frontpage("/")

    def do_GET(self):
        """
        Returns a requested HDF5 from temporary directory or the web frontend
        if the given request path was located outside the servers tmp directory.
        """
        log = self._logger
        km = KMHTTPRequestHandler._km
        if self.path == '/' or self.path.startswith('/../') or \
                self.path.startswith('/?'):
            km.web_interface.get_frontpage(self.path).sendTo(self)
        elif self.path.startswith(HTTP_REQUEST_DC_DETAILS_PATH):
            km.web_interface.get_details(self.path).sendTo(self)
        elif self.path.startswith(HTTP_REQUEST_SEARCH):
            km.web_interface.get_search(self.path).sendTo(self)
        else:
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
                try:
                    log.debug("Trying to remove temporary file '%s'..", f.name)
                    os.remove(f.name)
                except Exception:
                    log.warn("Cannot delete temporary file '%s'.", f.name)

    def send_head(self): # see SimpleHTTPServer.SimpleHTTPRequestHandler
        """
        Sends HTTP headers for HDF5 file requests.
        """
        log = self._logger
        km = KMHTTPRequestHandler._km
        source_dir = km._http_dir # this is intended
        log.debug("HTTP GET request: Reading files from directory '%s'..",
                  source_dir)
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
        #self.send_header("Content-type", "application/x-hdf")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f


def _enableLogging():
    """
    Enables logging to stdout for debug purposes.
    """
    l = logging.getLogger("pyphant")
    l.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s [%(name)s|%(levelname)s] %(message)s')
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(f)
    l.addHandler(h)
    l.info("Logger 'pyphant' has been configured for debug purposes.")
