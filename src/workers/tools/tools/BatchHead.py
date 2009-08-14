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
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, Param)
from pyphant.core.KnowledgeManager import KnowledgeManager as KM
from pyphant.core.Helpers import utf82uc

PARAMBY = [u"don't map",
           u"source/dest",
           u"columns of input SC"]


class BatchHead(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "BatchHead"
    _isBatchHead = True
    _params = [("paramMethod", "Map parameters via", PARAMBY, None),
               ("paramSource", "Parameter source", [u"None"], None),
               ("paramDestWorker", "Parameter destination worker",
                [u"None"], None),
               ("paramDest",
                "Parameter destination (OK to update)", [u"None"], None),
               ("paramConvert", "Convert parameter to string", False, None),
               ("requestedEmd5", "Do not change!", "First", None)]
    _sockets = [("inputSC", Connectors.TYPE_ARRAY)]

    def refreshParams(self, subscriber = None):
        wlist = self.parent.getWorkers()
        self.paramParamDestWorker.possibleValues = \
            [utf82uc(worker.getParam('name').value) for worker in wlist]
        if self.socketInputSC.isFull():
            tempSC = self.socketInputSC.getResult(subscriber)
            self.paramParamSource.possibleValues = \
                [utf82uc(key) for key in tempSC.longnames.keys()]
        try:
            pardest = self.parent.getWorker(
                self.paramParamDestWorker.value).getParamList()
            destlist = [utf82uc(param.name) for param in pardest]
        except:
            destlist = [u"None"]
        self.paramParamDest.possibleValues = destlist

    @Worker.plug(Connectors.TYPE_IMAGE)
    def execute(self, inputSC, subscriber = 0):
        km = KM.getInstance()
        emd5 = self.paramRequestedEmd5.value
        if emd5 == "First":
            emd5 = inputSC['emd5'].data[0]
        return km.getDataContainer(emd5)
