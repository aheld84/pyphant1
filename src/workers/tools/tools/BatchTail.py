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
from copy import deepcopy
from pyphant.core.DataContainer import FieldContainer
import numpy
from pyphant.core.Helpers import utf82uc
from pyphant.core.KnowledgeManager import KnowledgeManager

def getBatchHeads(recipe):
    bhs = filter(lambda x: hasattr(x, '_isBatchHead'), recipe.getWorkers())
    if bhs == []:
        return [u"None"]
    return [utf82uc(bh.getParam('name').value) for bh in bhs]

def batch(recipe, plug, head):
    inputSC = head.getSocket('inputSC').getResult()
    input_emd5s = inputSC['emd5'].data
    output_emd5s = []
    paramMethod = head.paramParamMethod.value
    paramConvert = head.paramParamConvert.value
    from tools.BatchHead import PARAMBY
    if paramMethod == PARAMBY[1]:
        paramSource = head.paramParamSource.value
        paramDestWorker = recipe.getWorker(head.paramParamDestWorker.value)
        paramDest = paramDestWorker.getParam(head.paramParamDest.value)
        paramFC = inputSC[paramSource]
        params = [val * paramFC.unit for val in paramFC.data]
        if paramConvert:
            params = [param.__str__() for param in params]
    rowcount = 0
    km = KnowledgeManager.getInstance()
    for input_emd5 in input_emd5s:
        if paramMethod == PARAMBY[1]:
            paramDest.value = params[rowcount]
        head.paramRequestedEmd5.value = utf82uc(input_emd5)
        output_dc = plug.getResult()
        output_dc.seal()
        km.registerDataContainer(output_dc)
        output_emd5s.append(output_dc.id)
        rowcount += 1
    head.paramRequestedEmd5.value = "First"
    outputSC = deepcopy(inputSC)
    output_columns = []
    for col in outputSC.columns:
        if col.longname == 'emd5':
            output_columns.append(FieldContainer(numpy.array(output_emd5s),
                                                 longname='emd5'))
        else:
            output_columns.append(col)
    outputSC.columns = output_columns
    outputSC.seal()
    return outputSC


class BatchTail(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "BatchTail"
    _params = [("head", "Select BatchHead", [u"None"], None)]
    _sockets = [("dummyDC", Connectors.TYPE_IMAGE)]

    def refreshParams(self, subscriber = None):
        self.paramHead.possibleValues = getBatchHeads(self.parent)
        recipe = self.parent
        if self.paramHead.value != u"None":
            head = recipe.getWorker(self.paramHead.value)
            socket = self.getSocket('dummyDC')
            plug = socket.getPlug()
            assert plug != None
            self.result = batch(recipe, plug, head)

    @Worker.plug(Connectors.TYPE_ARRAY)
    def execute(self, dummyDC, subscriber = 0):
        return self.result
