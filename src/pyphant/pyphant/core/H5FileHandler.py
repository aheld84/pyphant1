# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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
This module provides the H5FileHandler class.
"""
__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$:
import tables
from pyphant.core import DataContainer
from tables import StringCol
from pyphant.quantities.PhysicalQuantities import Quantity
import scipy
import logging
import os
from pyphant.core import PyTablesPersister
_logger = logging.getLogger("pyphant")


class H5FileHandler(object):
    """
    This class is used to handle IO operations on HDF5 files.
    """
    def __init__(self, filename, mode = 'a'):
        """
        Opens a HDF5 file.
        filename -- path to the file that should be opened
        mode -- mode in which file is opened. Possible values: 'r', 'w', 'a'
                meaning 'read only', 'overwrite' and 'append'.
                'a' is only allowed for files that are valid HDF5 files
                already.
        """
        assert mode in ['r', 'w', 'a']
        exists = os.path.isfile(filename)
        if mode == 'r' and not exists:
            raise IOError("File '%s' does not exist!"%(filename, ))
        self.filename = filename
        self.mode = mode
        if mode == 'w':
            tmphandle = tables.openFile(self.filename, 'w')
            tmphandle.close()
            self.mode = 'a'
        self.handle = None

    def __enter__(self):
        assert self.handle ==  None
        self.handle = tables.openFile(self.filename, self.mode)
        return self

    def __exit__(self, type, value, traceback):
        if self.handle != None:
            self.handle.close()
            self.handle = None

    def getNodeAndTypeFromId(self, dcId):
        """
        Returns a tuple (HDF5 node, uriType) for the given
        DataContainer emd5.
        dcId -- emd5 of the DataContainer
        """
        dcHash, uriType = DataContainer.parseId(dcId)
        try:
            resNode = self.handle.getNode("/results/result_" + dcHash)
        except (AttributeError, tables.NoSuchNodeError):
            raise AttributeError("Container %s not found in file %s."
                                 % (dcId, self.filename))
        if isinstance(uriType, unicode):
            uriType = uriType.encode('utf-8')
        return (resNode, uriType)

    def loadDataContainer(self, dcId):
        """
        Loads a DataContainer from the HDF5 file and returns it as a
        DataContainer instance.
        dcId -- emd5 of the DC to be returned
        """
        resNode, uriType = self.getNodeAndTypeFromId(dcId)
        if uriType == 'field':
            _logger.info("Trying to load field data from node %s..." % resNode)
            result = self.loadField(resNode)
            _logger.info("...successfully loaded.")
        elif uriType == 'sample':
            _logger.info("Trying to load sample data from node %s..." % resNode)
            result = self.loadSample(resNode)
            _logger.info("...successfully loaded.")
        else:
            raise TypeError, "Unknown result uriType in <%s>" % resNode._v_title
        return result

    def loadField(self, resNode):
        """
        Loads a FieldContainer from the given node and returns it as an
        instance. This method is intended for internal use only.
        resNode -- node at which the FieldContainer is located in the file.
        """
        return PyTablesPersister.loadField(self.handle, resNode)

    def loadSample(self, resNode):
        """
        Loads a SampleContainer from the given node and returns it as an
        instance. This method is intended for internal use only.
        resNode -- node at which the SampleContainer is located in the file.
        """
        return PyTablesPersister.loadSample(self.handle, resNode)

    def loadSummary(self, dcId = None):
        """
        Extracts meta data about a given DataContainer and returns it
        as a dictionary.
        dcId -- emd5 of the DC to summarize. If dcId == None, a dictionary
                that maps emd5s to summaries is returned.
        """
        if dcId == None:
            summary = {}
            for group in self.handle.walkGroups(where = "/results"):
                currDcId = group._v_attrs.TITLE
                if len(currDcId) > 0:
                    summary[currDcId] = self.loadSummary(currDcId)
        else:
            summary = {}
            summary['id'] = dcId
            resNode, uriType = self.getNodeAndTypeFromId(dcId)
            summary['longname'] = unicode(self.handle.getNodeAttr(resNode,
                                          "longname"), 'utf-8')
            summary['shortname'] = unicode(self.handle.getNodeAttr(resNode,
                                           "shortname"), 'utf-8')
            emd5_split = dcId.split('/')
            try:
                summary['machine'] = unicode(self.handle.getNodeAttr(resNode,
                                             "machine"), 'utf-8')
                summary['creator'] = unicode(self.handle.getNodeAttr(resNode,
                                             "creator"), 'utf-8')
            except:
                summary['machine'] = unicode(emd5_split[2], 'utf-8')
                summary['creator'] = unicode(emd5_split[3], 'utf-8')
            summary['date'] = unicode(emd5_split[4], 'utf-8')
            summary['hash'] = emd5_split[5].split('.')[0]
            summary['type'] = unicode(emd5_split[5].split('.')[1], 'utf-8')
            attributes = {}
            if uriType == 'field':
                for key in resNode.data._v_attrs._v_attrnamesuser:
                    attributes[key]=self.handle.getNodeAttr(resNode.data, key)
                unit = eval(unicode(self.handle.getNodeAttr(resNode, "unit"),
                                    'utf-8'))
                try:
                    if isinstance(unit, (str, unicode)):
                        unit = unit.replace('^', '**')
                    if isinstance(unit, unicode):
                        unit = unit.encode('utf-8')
                    summary['unit'] = Quantity(unit)
                except:
                    try:
                        summary['unit'] = Quantity("1" + unit)
                    except:
                        summary['unit'] = unit
                try:
                    dimTable = resNode.dimensions
                    dimensions = [self.loadSummary(row['id'])
                                  for row in dimTable.iterrows()]
                except tables.NoSuchNodeError:
                    dimensions = u'INDEX'
                    summary['type'] = u'index'
                summary['dimensions'] = dimensions
            elif uriType == 'sample':
                for key in resNode._v_attrs._v_attrnamesuser:
                    if key not in PyTablesPersister._reservedAttributes:
                        attributes[key] = self.handle.getNodeAttr(resNode, key)
                columns = []
                for resId in self.handle.getNodeAttr(resNode, "columns"):
                    nodename = "/results/" + resId
                    columnId = self.handle.getNodeAttr(nodename, "TITLE")
                    columns.append(self.loadSummary(columnId))
                summary['columns'] = columns
            summary['attributes'] = attributes
        return summary

    def saveDataContainer(self, result):
        """
        Saves a given DataContainer instance to the HDF5 file.
        The DataContainer has to be sealed or at least provide a valid
        emd5 in its '.id' attribute.
        A HDF5 group path that points to the location the DC was stored at
        is returned.
        result -- sealed DC instance
        """
        dcHash, uriType = DataContainer.parseId(result.id)
        resId = u"result_" + dcHash
        try:
            resultGroup = self.handle.getNode("/results/"+resId)
        except tables.NoSuchNodeError:
            try:
                resultGroup = self.handle.createGroup("/results", resId,
                                                      result.id.encode("utf-8"))
            except tables.NoSuchNodeError:
                self.handle.createGroup('/', 'results')
                resultGroup = self.handle.createGroup("/results", resId,
                                                      result.id.encode("utf-8"))
            if uriType == 'field':
                self.saveField(resultGroup, result)
            elif uriType == 'sample':
                self.saveSample(resultGroup, result)
            else:
                raise KeyError, "Unknown UriType %s in saving result %s."\
                    % (uriType, result.id)
        return resId

    def saveSample(self, resultGroup, result):
        """
        Saves a SampleContainer instance to the given node. This method is
        intended for internal use only.
        resultGroup -- node at which the SampleContainer should be saved
                       in the file.
        result -- SampleContainer instance to be saved
        """
        PyTablesPersister.saveSample(self.handle, resultGroup, result)

    def saveField(self, resultGroup, result):
        """
        Saves a FieldContainer instance to the given node. This method is
        intended for internal use only.
        resultGroup -- node at which the FieldContainer should be saved
                       in the file.
        result -- FieldContainer instance to be saved
        """
        PyTablesPersister.saveField(self.handle, resultGroup, result)
