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

"""Knowledge Manager for Pyphant
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
Use the data container!"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from pyphant.core.singletonmixin import Singleton
from pyphant.core.DataContainer import parseId
import pyphant.core.PyTablesPersister as ptp
from types import TupleType, StringTypes
import urllib
import cgi
import tempfile
import tables
import sys
import os, os.path
import logging
import traceback
from SocketServer import ThreadingMixIn
import threading
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from uuid import uuid1
import HTMLParser
from types import DictType
import re
import time
from urlparse import urlparse
from pyphant.core.H5FileHandler import H5FileHandler

WAITING_SECONDS_HTTP_SERVER_STOP = 5
HTTP_REQUEST_DC_URL_PATH="/request_dc_url"
HTTP_REQUEST_KM_ID_PATH="/request_km_id"
HTTP_REQUEST_DC_SUMMARY_PATH="/request_dc_summary"
HTML_BODY_INDEX = """<h1>Pyphant Web Frontend at %s</h1>
<form action="%s" method="post" enctype="text/plain" target="_blank">
Get DataContainer by emd5:
 <input type="text" size="50" maxlength="1000" name="dcid">
<input type="hidden" name="lastkmidindex" value="-1">
<input type="submit" name="submitbutton" value="GO">
</form>
<hr>
<h2>Registered KnowledgeManagers:</h2>
%s
<hr>
<h2>Registered DataContainers:</h2>
%s
<hr>
"""
# Maximum number of DCs to store in cache:
CACHE_SIZE = 50
# Timeout for cached DCs in seconds:
CACHE_TIMEOUT = 3600
# Number of hits a DC has to have at least in order to be cached:
CACHE_THRESHHOLD = 2
KM_PATH = '/KMstorage/'
REHDF5 = re.compile(r'..*\.h5$|..*\.hdf$|..*\.hdf5$')

def getPyphantPath(subdir = '/'):
    """returns full pyphant path with optional subdirectory
    subdir -- subdirectory that is created if it does not exist already,
              recursive creation of directories is supported also."""
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

def getFilenameFromDcId(dcId):
    """Returns a unique filename for the given emd5."""
    emd5list = urlparse(dcId + '.h5')[2][2:].split('/')
    emd5path = ''
    for p in emd5list:
        emd5path += (p + '/')
    emd5path = emd5path[:-1]
    directory = os.path.dirname(emd5path)
    filename = os.path.basename(emd5path)
    return getPyphantPath(KM_PATH + 'by_emd5/' + directory) + filename


class KnowledgeManagerException(Exception):
    def __init__(self, message, parent_excep=None, *args, **kwds):
        super(KnowledgeManagerException, self).__init__(message, *args, **kwds)
        self._message = message
        self._parent_excep = parent_excep

    def __str__(self):
        return self._message+" (reason: %s)" % (str(self._parent_excep),)

    def getParentException(self):
        return self._parent_excep


class KnowledgeManager(Singleton):
    def __init__(self):
        super(KnowledgeManager, self).__init__()
        self._logger = logging.getLogger("pyphant")
        self._storage = {}
        self._cache = {}
        self.H5FileHandlers = {}
        self._remoteKMs = {} # key:id, value:url
        self._server = None
        self._server_id = uuid1()
        self.restoreKnowledge()

    def __del__(self):
        if self.isServerRunning():
            self.stopServer()
        for handler in self.H5FileHandlers.itervalues():
            del handler

    def registerH5(self, filename, mode = 'a', registerContents = True):
        """Adds the given HDF5 file to the pool and handles all
        further IO operations on the given file in a save way. If you want the
        knowledge to be stored permanently, use registerURL.
        Possible usage: Register a file that does not exist (setting
        registerContents to False). It then is created.
        Get its H5FileHandler using the getH5FileHandler method.
        Use this FileHandler to write some Data to the file.
        Use the refreshH5 method to import the new contents into the
        KnowledgeManager.
        filename -- path to the HDF5 file to be registered.
        mode -- see H5FileHandler
        registerContents -- whether to register contents of the file as well."""
        if self.H5FileHandlers.has_key(filename):
            raise KnowledgeManagerException("'%s' has already been registered."\
                                                % (filename,))
        self.H5FileHandlers[filename] = H5FileHandler(filename, mode)
        if registerContents:
            self.refreshH5(filename)

    def getH5FileHandler(self, filename):
        """Returns a H5FileHandler for the given filename to perform IO
        operations on the file in a save way. The file has
        to be registered first using registerH5.
        As soon as you are done with your IO operations, use refreshH5
        in order to update the changes.
        filename -- path to the HDF5 file"""
        if self.H5FileHandlers.has_key(filename):
            return self.H5FileHandlers[filename]
        else:
            raise KnowledgeManagerException("'%s' has not been registered.")

    def refreshH5(self, filename):
        """Refreshes the contents of the given file. The file has to be
        registered first using registerH5. If a DC emd5 is found that is
        already known to the KnownledgeManager, it is not updated, following
        the principle that emd5s are unique and DCs that have been given a emd5
        should not me modified any more in any way.
        filename -- path to the HDF5 file"""
        h5fh = self.getH5FileHandler(filename)
        summaryDict = h5fh.loadSummary()
        for dcId, summary in summaryDict.items():
            if not self._storage.has_key(dcId):
                self._storage[dcId] = {'lasthit':None,
                                       'hitcount':0,
                                       'filehandler':h5fh,
                                       'summary':summary}

    def restoreKnowledge(self):
        """Restores knowledge from pyphant path"""
        def walkfiles(arg, dirname, fnames):
            for fname in fnames:
                if REHDF5.match(fname.lower()) != None:
                    if dirname.endswith('/'):
                        dirname = dirname[:-1]
                    self.registerH5(dirname + '/' + fname)
        os.path.walk(getPyphantPath(KM_PATH), walkfiles, None)

    def getSummary(self, dcId = None):
        """Behaves like H5FileHandler.loadSummary(dcId) except that for
        dcId == None all DataContainers that are stored locally are browsed."""
        if dcId == None:
            summary = {}
            for emd5, dcInfo in self._storage.iteritems():
                summary[emd5] = dcInfo['summary']
        else:
            if not self._storage.has_key(dcId):
                raise KnowledgeManagerException("DC with ID '%s' is unknown."\
                                                    % (dcId, ))
            dcInfo = self._storage[dcId]
            summary = dcInfo['summary']
        return summary

    def _getServerURL(self):
        if self._server is None:
            return None
        return "http://%s:%d" % (self._http_host, self._http_port)

    def getServerId(self):
        """Return uniqe id of the KnowledgeManager as uuid URN.
        """
        return self._server_id.urn

    def startServer(self, host = '127.0.0.1', port = 8000,
                    provide_web_frontend = True):
        """Start the HTTP server. When the server was running already,
        it is restartet with the new parameters.
        A temporary directory is generated in order to
        save temporary HDF5 files.
        The data may be announced to other KnowledgeManagers.
        host -- full qualified domain name or IP address under which
                server can be contacted via HTTP, default: '127.0.0.1'
        port -- port of HTTP server (integer), default: 8000
        provide_web_frontend -- whether to provide web frontend"""
        logger = self._logger
        if self.isServerRunning():
            logger.warn("Server is running at host %s, port %d already. \
Stopping server...", self._http_host, self._http_port)
            self.stopServer()
        self._provide_web_frontend = provide_web_frontend
        self._http_host = host
        self._http_port = port
        self._http_dir = tempfile.mkdtemp(prefix = 'pyphant-knowledgemanager')
        self._server = _HTTPServer((host, port), _HTTPRequestHandler)
        class _HTTPServerThread(threading.Thread):
            def run(other):
                self._server.start()
        self._http_server_thread = _HTTPServerThread()
        self._http_server_thread.start()
        self._logger.debug("Started HTTP server. Host: %s, port: %d, \
temp dir: %s", host, port, self._http_dir)

    def stopServer(self):
        """Stop the HTTP server. The temporary directory is removed."""
        logger = self._logger
        if self.isServerRunning():
            self._server.stop_server = True
            # do fake request
            try:
                urllib.urlopen(self._getServerURL())
            except:
                logger.warn("Fake HTTP request failed when stopping HTTP \
server.")
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
            except Exception, e:
                logger.warn("Failed to delete temporary directory '%s'.",
                            self._http_dir)
            self._http_dir = None
        else:
            self._logger.warn("HTTP server should be stopped but isn't \
running.")

    def isServerRunning(self):
        """Return whether HTTP server is running."""
        return self._server is not None

    def registerKnowledgeManager(self, host, port = 8000,
                                 share_knowledge = False):
        """Register a knowledge manager. The remote KnowledgeManager is
        contacted immediately in order to save its unique ID.
        host -- full qualified domain name or IP address at which
                server can be contacted via HTTP
        port -- port of HTTP server (integer), default: 8000
        share_knowledge -- local knowledge is made available to the remote KM
                           when set to True and the HTTP server is running at
                           the local KM, default: False"""
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
            answer = urllib.urlopen(km_url+HTTP_REQUEST_KM_ID_PATH, post_data)
            logger.debug("Info from HTTP answer: %s", answer.info())
            htmltext = answer.read()
            parser = _HTMLParser()
            parser.feed(htmltext)
            km_id = parser.headitems['pyphant']['kmid'].strip()
            answer.close()
            logger.debug("KM ID read from HTTP answer: %s", km_id)
        except Exception, e:
            raise KnowledgeManagerException(
                "Couldn't get ID for knowledge manager under URL %s."\
                    % (km_url,),e)
        self._remoteKMs[km_id] = km_url

    def registerURL(self, url):
        """Register an HDF5 file downloadable from given URL and store it
        permanently in the .pyphant directory. The files content is made
        available to the KnowledgeManager.
        url -- URL of the HDF5 file"""
        parsed = urlparse(url)
        filename = KM_PATH + 'registered/' + parsed[1] + '/'\
            + os.path.basename(parsed[2])
        directory = os.path.dirname(filename)
        filename = getPyphantPath(directory) + os.path.basename(filename)
        if REHDF5.match(filename) == None:
            filename += '.h5'
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
        self._logger.info("Retrieving url '%s'..." % (url,))
        self._logger.info("Using local file '%s'." % (filename,))
        savedto, headers = urllib.urlretrieve(url, filename)
        self._logger.info("Header information: %s", (str(headers),))
        self.registerH5(filename)

    def registerDataContainer(self, dc):
        """Register a DataContainer located in memory using a given
        reference and store it permanently.
        The DataContainer must have an .id attribute,
        which could be generated by the datacontainer.seal() method.
        If the DCs emd5 is already known to the KnowledgeManager,
        the DC is not registered again since emd5s are unique.
        dc -- reference to the DataContainer object"""
        if dc.id == None:
            raise KnowledgeManagerException("Invalid id for DataContainer '"\
                                            + dc.longname + "'")
        if not self._storage.has_key(dc.id):
            filename = getFilenameFromDcId(dc.id)
            self.registerH5(filename, 'w', False)
            handler = self.getH5FileHandler(filename)
            handler.saveDataContainer(dc)
            self.refreshH5(filename)

    def _getDCURLFromRemoteKMs(self, query_dict):
        """Return URL for a DataContainer by requesting remote
        KnowledgeManagers.
        query_dict -- see _getDataContainerURL"""
        logger = self._logger
        # add this KM to query
        query_dict['lastkmidindex'] += 1
        query_dict['kmid%d'%(query_dict['lastkmidindex'],)] = self.getServerId()
        # ask every remote KnowledgeManager for id
        logger.debug("Requesting knowledge managers for DC id '%s'..."\
                     % (query_dict['dcid'],))
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
                        parser = _HTMLParser()
                        htmltext = answer.read()
                        parser.feed(htmltext)
                        dc_url = parser.headitems['pyphant']['hdf5url'].strip()
                        logger.debug("URL for id read from HTTP answer: %s",
                                     dc_url)
                        break
                    elif code == 404:
                        # update query_dict:
                        parser = _HTMLParser()
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
        """Return a URL from which a DataContainer can be downloaded.
        The server must be running before calling this method.
        query_dict -- dict of DC ID to get and KnowledgeManager IDs
                      which shouldn't be asked.
                      e.g.: {'dcid':'somedcid',
                             'lastkmidindex:1',
                             'kmid0':'someid',
                             'kmid1':'anotherid'}
                      query_dict is extended by this method in order to
                      exclude KMs recursively."""
        assert self.isServerRunning(), "Server is not running."
        dc_id = query_dict['dcid']
        if self._storage.has_key(dc_id):
            dc = self.getDataContainer(dc_id, True, False)
            # Wrap data container in temporary HDF5 file
            osFileId, filename = tempfile.mkstemp(suffix = '.h5',
                                                  prefix = 'dcrequest-',
                                                  dir = self._http_dir)
            os.close(osFileId)
            handler = H5FileHandler(filename, 'w')
            handler.saveDataContainer(dc)
            del handler
            dc_url = self._getServerURL() + "/" + os.path.basename(filename)
        else:
            try:
                dc_url = self._getDCURLFromRemoteKMs(query_dict)
            except Exception, e:
                raise KnowledgeManagerException(
                    "URL for DC ID '%s' not found." % (dc_id,), e)
        return dc_url

    def getDataContainer(self, dc_id, use_cache=True, try_remote=True):
        """Returns DataContainer matching the given id.
        dc_id -- Unique ID of the DataContainer (emd5)
        use_cache -- Try local cache first and cache DC for further
                     lookups (default: True)
        try_remote -- Try to get DC from remote KMs (default: True)"""
        dc = None
        found_in_cache = False
        islocal = self._storage.has_key(dc_id)
        if islocal:
            dcinfo = self._storage[dc_id]
            now = time.time()
            if dcinfo['lasthit'] != None:
                if (now - dcinfo['lasthit']) >= CACHE_TIMEOUT:
                    dcinfo['hitcount'] = 0
            dcinfo['lasthit'] = now
            dcinfo['hitcount'] += 1
            if use_cache:
                if self._cache.has_key(dc_id):
                    dc = self._cache[dc_id]
                    found_in_cache = True
                    self._logger.debug("DC with ID '%s' found in cache.", dc_id)
                else:
                    self._logger.debug("DC with ID '%s' not found in cache.",
                                       dc_id)
            if not found_in_cache:
                try:
                    dc = dcinfo['filehandler'].loadDataContainer(dc_id)
                except Exception, e:
                    raise KnowledgeManagerException("DC ID '%s' known, but \
cannot be read from file '%s'." % (dc_id,localfilename), e)
                if use_cache and dcinfo['hitcount'] >= CACHE_THRESHHOLD:
                    docache = False
                    if len(self._cache) >= CACHE_SIZE:
                        minhitcount = sys.maxint
                        for cachedid, cacheddcinfo in self._cache.iteritems():
                            if (now - cacheddcinfo['lasthit']) >= CACHE_TIMEOUT:
                                cacheddcinfo['hitcount'] = 0
                                self._cache.pop(cachedid)
                                docache = True
                                break
                            elif cacheddcinfo['hitcount'] < minhitcount:
                                minhitcount = cacheddcinfo['hitcount']
                        if docache == False \
                                and dcinfo['hitcount'] > minhitcount:
                            docache == True
                    else:
                        docache = True
                    if docache:
                        self._cache[dc_id] = dc
                        self._logger.debug("Cached DC with ID '%s'", dc_id)
        elif try_remote:
            dc_url = self._getDCURLFromRemoteKMs({'dcid':dc_id,
                                                  'lastkmidindex':-1})
            if dc_url == None:
                raise KnowledgeManagerException("DC ID '%s' is unknown."\
                                                    %(dc_id,))
            filename = getFilenameFromDcId(dc_id)
            savedto, headers = urllib.urlretrieve(dc_url, filename)
            self.registerH5(filename)
            dc = self.H5FileHandlers[filename].loadDataContainer(dc_id)
        else:
            raise KnowledgeManagerException("DC ID '%s' is unknown." % (dc_id,))
        return dc


class _HTTPRequestHandler(SimpleHTTPRequestHandler):
    _knowledge_manager = KnowledgeManager.getInstance()
    _logger = logging.getLogger("pyphant")

    def send_response(self, code, message=None):
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
        self._logger.debug("POST request from client (host,port): %s",
                           self.client_address)
        self._logger.debug("POST request path: %s", self.path)
        if self.path==HTTP_REQUEST_DC_URL_PATH:
            httpanswer = self._do_POST_request_dc_url()
        elif self.path==HTTP_REQUEST_KM_ID_PATH:
            httpanswer = self._do_POST_request_km_id()
        else:
            code = 400
            message = "Unknown request path '%s'." % (self.path,)
            httpanswer = _HTTPAnswer(code, message)
        httpanswer.sendTo(self)

    def _do_POST_request_km_id(self):
        """Return the KnowledgeManager ID."""
        km = _HTTPRequestHandler._knowledge_manager
        if self.headers.has_key('content-length'):
            length= int( self.headers['content-length'] )
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
        return _HTTPAnswer(200, None, {}, 'text/html',
                           {'pyphant':{'kmid':km.getServerId()}},
                           "Server ID is: %s" % (km.getServerId(), ))

    def _do_POST_request_dc_url(self):
        """Return a URL for a given DataContainer ID."""
        if self.headers.has_key('content-length'):
            length= int( self.headers['content-length'] )
            query = self.rfile.read(length)
            tmp_dict = cgi.parse_qs(query)
            query_dict = dict([(k, v[0]) for (k, v) in tmp_dict.items()\
                               if (k.startswith('kmid')\
                               or k == 'lastkmidindex' or k =='dcid')])
            query_dict['lastkmidindex'] = int(query_dict['lastkmidindex'])
            self._logger.debug("Query dict: %s", str(query_dict))
            try:
                km = _HTTPRequestHandler._knowledge_manager
                redirect_url = km._getDataContainerURL(query_dict)
                if redirect_url != None:
                    self._logger.debug("Returning URL '%s'...", redirect_url)
                    httpanswer\
                        = _HTTPAnswer(201,
                                      None,
                                      {'location':redirect_url},
                                      'text/html',
                                      {'pyphant':{'hdf5url':redirect_url},
                                       'title':"DC ID '%s'"\
                                               % (query_dict['dcid'], )},
                                      "Download DataContainer with ID '%s' as \
<a href=\"%s\">HDF5</a>" % (query_dict['dcid'], redirect_url))
                else:
                    self._logger.debug("Returning Error Code 404: \
DataContainer ID '%s' not found.", query_dict['dcid'])
                    message = "DataContainer ID '%s' not found. Returning \
updated query in HTML head." % (query_dict['dcid'], )
                    htmlheaders = {'pyphant':dict(query_dict)}
                    htmlheaders['pyphant']['lastkmidindex']\
                        = str(htmlheaders['pyphant']['lastkmidindex'])
                    self._logger.debug('Returning html header: %s',
                                       str(htmlheaders))
                    htmlbody = "DataContainer ID '%s' not found."\
                               % (query_dict['dcid'],)
                    httpanswer = _HTTPAnswer(404,
                                             message,
                                             {},
                                             'text/html',
                                             htmlheaders,
                                             htmlbody,
                                             False)
            except Exception, e:
                self._logger.warn("Catched exception: %s",
                                  traceback.format_exc())
                httpanswer = _HTTPAnswer(500,
                                         "Internal server error occured during \
lookup of DataContainer with ID '%s'" % (query_dict['dcid'], ))
        else:
            httpanswer = _HTTPAnswer(400, "Cannot interpret query.")
        return httpanswer

    def do_GET(self):
        """Return a requested HDF5 from temporary directory."""
        log = self._logger
        km = _HTTPRequestHandler._knowledge_manager
        if self.path == '/' or self.path.startswith('/../'):
            if km._provide_web_frontend:
                rKMshtmldict = _HTMLDict("URL", "ID")
                for id, url in km._remoteKMs.iteritems():
                    rKMshtmldict[_HTMLLink(url, url, "_blank")] = id
                shtmldict = _HTMLDict("Longname", "Summary")
                summarydict = km.getSummary()
                for summary in summarydict.values():
                    shtmldict[_HTMLLink("NOTIMPLEMENTED",
                                        summary['longname'],
                                        "_blank")] = summary
                htmlbody = HTML_BODY_INDEX % (km._getServerURL(),
                                              HTTP_REQUEST_DC_URL_PATH,
                                              rKMshtmldict.getHTML(),
                                              shtmldict.getHTML())
                httpanswer = _HTTPAnswer(200,
                                         None,
                                         {},
                                         'text/html',
                                         {'title':'Pyphant Web Frontend at %s'\
                                                  %(km._getServerURL(), )},
                                         htmlbody)
                httpanswer.sendTo(self)
            else:
                httpanswer = _HTTPAnswer(200,
                                         None,
                                         {},
                                         'text/html',
                                         {},
                                         'The web frontend has not been \
started!')
                httpanswer.sendTo(self)
        else:
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
        """Send header for HDF5 file request."""
        log = self._logger
        km = _HTTPRequestHandler._knowledge_manager
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
        self.send_header("Content-type", "application/x-hdf")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f


class _HTTPServer(ThreadingMixIn,HTTPServer):
    """Threaded HTTP Server for the KnowledgeManager."""
    stop_server = False
    _logger = logging.getLogger("pyphant")

    def start(self):
        while not self.stop_server:
            self.handle_request()
        self._logger.info("Stopped HTTP server.")


class _HTMLDict(dict):
    def __init__(self, keylabel, valuelabel):
        self.keylabel = keylabel
        self.valuelabel = valuelabel

    def getHTML(self, printkeys = True):
        if printkeys:
            output = '<table border="2" width="100%%"><tr><th>%s</th>\
<th>%s</th></tr>\n'%(self.keylabel, self.valuelabel)
        else:
            output = '<table border="2" width="100%%"><tr><th>%s</th>\
</tr>\n'%(self.valuelabel, )
        for k, v in self.items():
            if hasattr(k, 'getHTML'):
                kout = k.getHTML()
            else:
                kout = str(k)
            if hasattr(v, 'getHTML'):
                vout = v.getHTML()
            else:
                vout = str(v)
            if printkeys:
                output += '<tr width="100%%"><td>%s</td><td>%s</td></tr>\n'\
                          % (kout, vout)
            else:
                output += '<tr width="100%%"><td>%s</td></tr>\n' % (vout, )
        output += '</table>\n'
        return output

    def setDict(self, d):
        self.clear()
        for k in d:
            self[k] = d[k]


class _HTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self._isinhead = False
        self._isinbody = False
        self.headitems = {} # tag : attributes
        self.bodytext = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self._isinhead = True
        elif tag == 'body':
            self._isinbody = True
        elif self._isinhead:
            attrsdict = {}
            for pairs in attrs:
                attrsdict[pairs[0]] = pairs[1]
            self.headitems[tag] = attrsdict

    def handle_startendtag(self, tag, attrs):
        if self._isinhead:
            attrsdict = {}
            for pairs in attrs:
                attrsdict[pairs[0]] = pairs[1]
            self.headitems[tag] = attrsdict

    def handle_endtag(self, tag):
        if tag == 'head':
            self._isinhead = False
        elif tag == 'body':
            self._isinbody = False

    def handle_data(self, data):
        if self._isinbody:
            self.bodytext += data


class _HTTPAnswer():
    def __init__(self,
                 code,
                 message = None,
                 httpheaders = {},
                 contenttype = 'text/html',
                 htmlheaders = {},
                 htmlbody = '',
                 senddefaulterrors = True):
        self._code = code
        self._message = message
        self._httpheaders = httpheaders
        self._htmlheaders = htmlheaders
        self._htmlbody = htmlbody
        self._httpheaders['Content-type'] = contenttype
        self._senddefaulterrors = senddefaulterrors

    def sendTo(self, handler):
        _logger = logging.getLogger("pyphant")
        if self._code >= 400 and self._senddefaulterrors:
            #send error response
            handler.send_error(self._code, self._message)
        else:
            #send HTTP headers...
            handler.send_response(self._code, self._message)
            for key, value in self._httpheaders.items():
                handler.send_header(key, value)
                _logger.debug("key: %s, value: %s\n", key, value)
            handler.end_headers()
            #send HTML headers...
            handler.wfile.write('<html>\n<head>\n')
            for tag, attrs in self._htmlheaders.items():
                if isinstance(attrs, DictType):
                    handler.wfile.write('<%s '%(tag, ))
                    for key, value in attrs.items():
                        handler.wfile.write('%s="%s" '% (key, value))
                    handler.wfile.write('>\n')
                else:
                    handler.wfile.write('<%s>%s</%s>\n'%(tag, attrs, tag))
            handler.wfile.write('</head>\n')
            #send HTML body...
            handler.wfile.write('<body>\n')
            handler.wfile.write(self._htmlbody+'\n')
            handler.wfile.write('</body></html>\n')
            handler.wfile.write('\n')


class _HTMLLink():
    def __init__(self, url, linktext, target = None):
        self._url = url
        self._linktext = linktext
        self._target = target

    def getHTML(self):
        targetstring = ""
        if self._target != None:
            targetstring = ' target="%s"'%(self._target, )
        return '<a href="%s"%s>%s</a>'\
               % (self._url, targetstring, self._linktext)

def _enableLogging():
    """Enable logging for debug purposes."""
    l = logging.getLogger("pyphant")
    l.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s [%(name)s|%(levelname)s] %(message)s')
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(f)
    l.addHandler(h)
    l.info("Logger 'pyphant' has been configured for debug purposes.")
