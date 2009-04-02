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
import tables
import os, os.path
import logging

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

    def _retrieveURL(self, url):
        # exceptions?
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

        return localfilename

    def registerURL(self, url):
        localfilename = self._retrieveURL(url)
           
    def registerDataContainer(self, datacontainer):
        try:
            assert datacontainer.id is not None
            self._refs[datacontainer.id] = datacontainer
        except Exception, e:
            raise KnowledgeManagerException("Invalid id for DataContainer '" +\
                                                datacontainer.longname+"'", e)

    #def searchAndRegisterKnowledgeManager(self, host)
    #    KM =remote object auf host
    #    registerKnowledgeManager(self, KM)
    #def registerKnowledgeManager(self, KM)

    def getDataContainer(self, id, try_cache=True):
        if id not in self._refs.keys():
            raise KnowledgeManagerException("Id '%s' unknown." % (id,))
            
        ref = self._refs[id]
        if isinstance(ref, TupleType):
            dc = self._getDCfromURLRef(id, try_cache = try_cache)
        else:
            dc = ref
            
        return dc

    def _getDCfromURLRef(self, id, try_cache=True):
        url, localfilename, h5path = self._refs[id]
        if not try_cache:
            os.remove(localfilename)

        if not os.path.exists(localfilename):
            localfilename = self._retrieveURL(url)
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
        return dc
