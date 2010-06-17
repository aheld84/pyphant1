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
This module provides the KnowledgeManager class as well as some helper
classes.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source: $

from pyphant.core.singletonmixin import Singleton
import tempfile
import os
import logging
import re
from pyphant.core.H5FileHandler import (H5FileHandler, im_id)
from fmfile import FMFLoader
from pyphant.core.SQLiteWrapper import (SQLiteWrapper, AnyValue)
from pyphant.core.Helpers import getPyphantPath
from uuid import uuid1
from urlparse import urlparse
import urllib

# Limit for sum(DC.rawDataBytes) for DC in cache:
CACHE_MAX_SIZE = 256 * 1024 * 1024
# Limit for number of stored DCs in cache:
CACHE_MAX_NUMBER = 100
KM_PATH = 'KMstorage'
REHDF5 = re.compile(r'..*\.h5$|..*\.hdf$|..*\.hdf5$')
REFMF = re.compile(r'..*\.fmf$')

def getFilenameFromDcId(dcId, temporary=False):
    """
    Returns a unique filename for the given emd5.
    """
    emd5list = (dcId + '.h5')[7:].split('/')
    emd5path = os.path.join(
        *(emd5list[:-2] + [emd5list[-2][:10],
                           emd5list[-2][11:] + '.' + emd5list[-1]]))
    #needed for windows version of pytables:
    emd5path = emd5path.replace(':', '.')
    directory = os.path.dirname(emd5path)
    filename = os.path.basename(emd5path)
    if temporary:
        subdir = os.path.join('tmp', 'by_emd5')
    else:
        subdir = 'by_emd5'
    return os.path.join(getPyphantPath(
        os.path.join(KM_PATH, subdir, directory)), filename)


class DCNotFoundError(Exception):
    pass


class CachedDC(object):
    """
    Class representing a cached DataContainer
    """
    def __init__(self, dc_ref):
        self.id = dc_ref.id
        self.ref = dc_ref
        self.size = dc_ref.rawDataBytes

    def __eq__(self, other):
        return self.id == other.id


class TestCachedDC(object):
    """
    Class representing a cache lookup
    """
    def __init__(self, dc_id):
        self.id = dc_id

    def __eq__(self, other):
        return self.id == other.id


KM_DBASE = u'default' # modify for debug purposes


class KnowledgeManager(Singleton):
    """
    Knowledge Manager for Pyphant
    =============================
    The ID of a DataContainer object is given by an emd5 string.
    Responsibilities:
    -----------------
    - Manage local storage of DataContainers
    - Resolve IDs to DC instances
    - Communicate with a KnowledgeNode in order to share Knowledge
      among other KM instances via HTTP.
    - Manage and search meta data for DataContainers
    Usage examples:
    ---------------
    Get a reference to the KnowledgeManager instance, which is a
    singleton:
    from pyphant.core.KnowledgeManager import KnowledgeManager
        km = KnowledgeManager.getInstance()
    Register a local HDF5 file:
        km.registerURL("/some_directory/data.h5")
    Register and persist a local HDF5 file:
        km.registerURL("file:///tmp/data.h5")
    Register and persist a remote FMF file:
        km.registerURL("http://example.com/repository/data.fmf")
    Request DataContainer by its id:
        dc = km.getDataContainer(id) # `dc` is an actual instance now
    For searching meta data see docstring of KM.search() below.
    How to share Knowledge:
        Hook up the KM to a KnowledgeNode, see documentation in the
        KnowledgeNode module.
    Known issues:
    ------------
    KM is NOT thread-safe yet.
    """
    def __init__(self):
        """
        Sets up the DataBase if it has not been initialized yet,
        sets up the cache and clears the tmp dir.
        Sets a uuid to identify the instance.
        """
        super(KnowledgeManager, self).__init__()
        self.logger = logging.getLogger("pyphant")
        self._cache = []
        self._cache_size = 0
        if KM_DBASE == u'default':
            self.dbase = os.path.join(getPyphantPath('sqlite3'),
                                      "km_meta.sqlite3")
        else:
            self.dbase = KM_DBASE
        self.any_value = AnyValue()
        self.node = None # for hooking up a KnowledgeNode
        self.uuid = uuid1().urn
        tmpdir = getPyphantPath(os.path.join(KM_PATH, 'tmp'))
        if os.path.isdir(tmpdir):
            from shutil import rmtree
            try:
                rmtree(tmpdir)
            except OSError:
                self.logger.warn("Could not delete '%s'." % tmpdir)
        with SQLiteWrapper(self.dbase) as wrapper:
            rebuild = wrapper.dbase_broken()
        if rebuild:
            self.logger.info("dbase needs rebuild")
            self.rebuildIndex()
        else:
            with SQLiteWrapper(self.dbase) as wrapper:
                wrapper.setup_sqlite()

    def rebuildIndex(self):
        self.logger.info("rebuilding dbase...")
        oldname = self.dbase + ".bak"
        if os.path.exists(oldname):
            os.remove(oldname)
        os.rename(self.dbase, oldname)
        with SQLiteWrapper(self.dbase) as wrapper:
            wrapper.setup_dbase()
        self.updateIndex()
        self.logger.info("done rebuilding dbase")

    def updateIndex(self):
        file_list = []
        def accumulate_files(flist, directory, files):
            for fname in [afname for afname in files if afname.endswith('.h5')]:
                flist.append(os.path.realpath(os.path.join(directory, fname)))
        os.path.walk(getPyphantPath(KM_PATH), accumulate_files, file_list)
        from wx import (ProgressDialog, PyNoAppError)
        try:
            pdial = ProgressDialog('Rebuilding index...', ' ' * 100,
                                   maximum=len(file_list))
        except PyNoAppError:
            pdial = None
        count = 1
        for realname in file_list:
            if pdial is not None:
                pdial.Update(count, os.path.basename(realname))
                count += 1
            try:
                self.registerH5(realname)
            except:
                self.logger.warn("Could not extract meta data from '%s'."\
                                 % realname)
        if pdial is not None:
            pdial.Destroy()

    def hasDataContainer(self, dcid):
        """
        Returns whether the given DC is stored locally.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            has_entry = wrapper.has_entry(dcid)
        return has_entry

    def isTemporary(self, dcid):
        """
        Returns whether the given DC is stored temporarily.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            is_tmp = wrapper.is_temporary(dcid)
        return is_tmp

    def setTemporary(self, dcid, temporary):
        """
        Sets the given entry to temporary, which means it will be
        deleted upon restart or removes the temporary flag.
        - dcid: emd5 of DataContainer
        - temporary: boolean
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            wrapper.set_temporary(dcid, temporary)

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
                if dcId == im_id:
                    wrapper.set_entry(summary, None, temporary)
                else:
                    wrapper.set_entry(summary, filename, temporary)

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
            tmp_extension = 'tmp'
        try:
            remote_path = parsed.path
        except AttributeError:
            remote_path = parsed[2]
        directory = os.path.join(KM_PATH, tmp_extension,
                                 'registered')
        filename = os.path.join(getPyphantPath(directory),
                                os.path.basename(remote_path))
        if os.path.exists(filename):
            i = 0
            directory = os.path.dirname(filename)
            basename = os.path.basename(filename)
            split = basename.split('.')
            ext = split.pop()
            fnwoext = ''
            for part in split:
                fnwoext += (part + '.')
            from sys import maxint
            while i < maxint:
                fill = str(i).zfill(10)
                tryfn = os.path.join(directory,
                                     "%s%s.%s" % (fnwoext, fill, ext))
                if os.path.exists(tryfn):
                    i += 1
                else:
                    filename = tryfn
                    break
        self.logger.info("Retrieving url '%s'..." % url)
        self.logger.info("Using local file '%s'." % filename)
        savedto, headers = urllib.urlretrieve(url, filename)
        if REFMF.match(filename.lower()) != None:
            self.registerFMF(filename, temporary)
        elif REHDF5.match(filename.lower()) != None:
            self.registerH5(filename, temporary)
        else:
            msg = "Could not guess type of '%s'" % url
            self.logger.error(msg)
            raise ValueError(msg)

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
            msg = "Missing id for DataContainer. DC has not been sealed."
            self.logger.error(msg)
            raise ValueError(msg)
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

    def getDataContainer(self, dc_id, use_cache=True, try_remote=True):
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
        elif try_remote and self.node != None:
            try:
                return self.node.get_datacontainer(dc_id)
            except DCNotFoundError:
                pass
        msg = "Could not find DC with id '%s'." % dc_id
        self.logger.error(msg)
        raise DCNotFoundError(msg)

    def getEmd5List(self):
        """
        returns a list with all locally known DataContainer ids.
        """
        with SQLiteWrapper(self.dbase) as wrapper:
            return wrapper.get_emd5_list()

    def search(self, result_keys, search_dict={}, order_by=None,
               order_asc=True, limit=-1, offset=0, distinct=False):
        """
        see SQLiteWrapper.get_andsearch_result
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
            rowwrapper = wrapper[dc_id]
            keys = list(SQLiteWrapper.all_keys)
            if dc_id.endswith('field'):
                keys.remove('columns')
            elif dc_id.endswith('sample'):
                keys.remove('unit')
                keys.remove('dimensions')
            summary = dict([(key, rowwrapper[key]) for key in keys])
        return summary
