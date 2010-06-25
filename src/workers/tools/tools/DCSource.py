# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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
This module provides a base class for FCSource and SCSource
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core.KnowledgeManager import KnowledgeManager
from pyphant.core.Param import (
    ParamChangeExpected, VisualizerChangeValue, ParamOverridden)
ANYSTR = u"-- any --"


class DCSource(object):
    """
    This is the base class for SCSource and FCSource. It has to
    be subclassed before use.
    """
    def __init__(self, dc_type):
        self.dc_type = dc_type
        self.expectedValues = {}
        for name, param in self._params.iteritems():
            if name == 'name':
                continue
            param.registerListener(self.onPCE, ParamChangeExpected)
            param.registerListener(self.onPO, ParamOverridden)
            self.expectedValues[name] = param.value

    def onPCE(self, event):
        if event.param.name == 'reset' and event.expectedValue:
            self.refreshParams(update=False, autoSelect=False, reset=True)
            vcv = VisualizerChangeValue(event.param, value=False)
            event.param._eventDispatcher.dispatchEvent(vcv)
        elif event.param.name != 'reset' and \
                 event.expectedValue != self.expectedValues[event.param.name]:
            self.expectedValues[event.param.name] = event.expectedValue
            autoSelect = event.expectedValue != ANYSTR
            self.refreshParams(update=False, autoSelect=autoSelect)

    def onPO(self, event):
        self.expectedValues[event.param.name] = event.newValue

    def getKeyValue(self, key, value, name):
        if key in ['col_of', 'dim_of', 'has_dim', 'has_col']:
            value = {'longname':value}
        return (key, value)

    def getSearchDict(self, name):
        search_dict = {'type':self.dc_type}
        search_dict.update(dict(
            [self.getKeyValue(key, val, name) \
             for key, val in self.expectedValues.iteritems() \
             if key not in ['name', 'reset', name] and val != ANYSTR]))
        if name == 'dim_of':
            search_dict = {'type':'field', 'has_dim':search_dict}
        elif name == 'col_of':
            search_dict = {'type':'sample', 'has_col':search_dict}
        elif name == 'has_dim':
            search_dict = {'type':'field', 'dim_of':search_dict}
        elif name == 'has_col':
            search_dict = {'col_of':search_dict}
        return search_dict

    def getResKey(self, name):
        if name in ['col_of', 'dim_of', 'has_col', 'has_dim']:
            return 'longname'
        else:
            return name

    def refreshParams(self, subscriber=None, update=True, autoSelect=True,
                      reset=False):
        if update:
            self.expectedValues = dict(
                [(name, param.value) for name, param \
                 in self._params.iteritems() if name not in ['name', 'reset']])
        elif reset:
            self.expectedValues = dict(
                [(name, ANYSTR) for name in self._params.iterkeys() \
                 if name not in ['name', 'reset']])
        kmanager = KnowledgeManager.getInstance()
        for name, param in self._params.iteritems():
            if name in ['name', 'reset']:
                continue
            search_dict = self.getSearchDict(name)
            newEVs = [[ANYSTR]]
            newEVs.extend(kmanager.search(
                [self.getResKey(name)], search_dict=search_dict, distinct=True))
            newEVs = [newEV[0] for newEV in newEVs]
            event = VisualizerChangeValue(param, possibleValues=newEVs,
                                          autoSelect=autoSelect)
            if reset:
                event.value = ANYSTR
            param._eventDispatcher.dispatchEvent(event)
            if update:
                param.possibleValues = newEVs
