# -*- coding: utf-8 -*-

# Copyright (c) 2007-2009, Rectorate of the University of Freiburg
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

u"""
"""

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, DataContainer)
import copy


class ColumnExtractor(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Extract Column"

    _sockets = [("osc", Connectors.TYPE_ARRAY)]
    _params = [("column", u"Column", [u"Absorption"], None),
               ("index", u"Row", 'All', None)]

    def refreshParams(self, subscriber=None):
        if self.socketOsc.isFull():
            templ = self.socketOsc.getResult( subscriber )
            self.paramColumn.possibleValues = templ.longnames.keys()

    @Worker.plug(Connectors.TYPE_IMAGE)
    def extract(self, osc, subscriber=0):
        col = osc[self.paramColumn.value]
        if self.paramIndex.value=='All':
            result = copy.deepcopy(col)
        else:
            index = int(self.paramIndex.value)
            if len(col.dimensions)>1:
                dim = col.dimensions[1]
            else:
                oldDim = col.dimensions[0]
                dim = DataContainer.FieldContainer(oldDim.data[index],
                                                   unit = oldDim.unit,
                                                   longname=oldDim.longname,
                                                   shortname=oldDim.shortname)
            data = col.maskedData[index]
            result = DataContainer.FieldContainer(data.data, mask=data.mask,
                                                  unit = col.unit,
                                                  dimensions = [dim],
                                                  longname=col.longname,
                                                  shortname=col.shortname)
        #result.attributes = osc.attributes
        result.attributes = col.attributes
        result.seal()
        return result
