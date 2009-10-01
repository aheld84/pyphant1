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
This module provides a worker for importing DataConainers from the
KnowledgeManager into wxPyphant.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors,
                          Param)
from pyphant.core.KnowledgeManager import KnowledgeManager as KM


class HiddenValue(unicode):
    def setHiddenValue(self, hiddenvalue):
        self.hiddenvalue = hiddenvalue


class Emd5Src(Worker.Worker):
    """
    This worker provides dropdown lists for selecting a DataContainer from
    the KnowledgeManaer.
    """
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Emd5Src"

    _params = [("selectby", u"select by:", [u"emd5",
                                            u"longname",
                                            u"shortname",
                                            u"enter emd5"], None),
               ("emd5", u"emd5:", [u"None"], None),
               ("longname", u"longname:", [u"None"], None),
               ("shortname", u"shortname:", [u"None"], None),
               ("enteremd5", u"enter emd5:", "", None)]

    def refreshParams(self, subscriber = None):
        km = KM.getInstance()
        emd5list = km.getEmd5List()
        lnlist = []
        snlist = []
        for emd5 in emd5list:
            summary = km.getSummary(emd5)
            if summary['type'] != u'index':
                info = u"%s '%s' (creator: %s, date: %s)"
                lnitem = HiddenValue(info\
                                         % (summary['type'],
                                            summary['longname'],
                                            summary['creator'],
                                            summary['date']))
                lnitem.setHiddenValue(emd5)
                lnlist.append(lnitem)
                snitem = HiddenValue(info\
                                         % (summary['type'],
                                            summary['shortname'],
                                            summary['creator'],
                                            summary['date']))
                snitem.setHiddenValue(emd5)
                snlist.append(snitem)
        emd5list.sort()
        lnlist.sort()
        snlist.sort()
        self.paramEmd5.possibleValues = emd5list
        self.paramLongname.possibleValues = lnlist
        self.paramShortname.possibleValues = snlist

    @Worker.plug(Connectors.TYPE_IMAGE)
    def load(self, subscriber = 0):
        km = KM.getInstance()
        if self.paramSelectby.value == u'emd5':
            emd5 = self.paramEmd5.value.encode('utf-8')
        elif self.paramSelectby.value == u'longname':
            emd5 = self.paramLongname.value.hiddenvalue
        elif self.paramSelectby.value == u'shortname':
            emd5 = self.paramShortname.value.hiddenvalue
        elif self.paramSelectby.value == u'enter emd5':
            emd5 = self.paramEnteremd5.value.encode('utf-8')
        return km.getDataContainer(emd5)
