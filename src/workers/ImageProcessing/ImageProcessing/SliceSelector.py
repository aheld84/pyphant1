# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param
from tools.Emd5Src import HiddenValue
import ImageProcessing


class SliceSelector(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "SliceSelector"
    _sockets = [("zstack", Connectors.TYPE_ARRAY)]
    _params = [("slice", u"ZSlice", [u'None'], None)]

    def refreshParams(self, subscriber=None):
        if self.socketZstack.isFull():
            repr_sc = self.socketZstack.getResult(subscriber)
            unit = repr_sc['z-value'].unit
            pvalues = []
            for zvalue, emd5 in zip(repr_sc['z-value'].data,
                                    repr_sc['emd5'].data):
                hvalue = HiddenValue(unicode((zvalue * unit).__str__()))
                hvalue.setHiddenValue(unicode(emd5))
                pvalues.append(hvalue)
            #pvalues.sort()
            self.paramSlice.possibleValues = pvalues

    @Worker.plug(Connectors.TYPE_IMAGE)
    def image(self, subscriber=0):
        img_id = self.paramSlice.value.hiddenvalue
        from pyphant.core.KnowledgeManager import KnowledgeManager
        kmanager = KnowledgeManager.getInstance()
        return kmanager.getDataContainer(img_id)
