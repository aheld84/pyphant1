# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009  Andreas W. Liehr (liehr@users.sourceforge.net)
# all rights reserved.
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
from pyphant.core.DataContainer import (FieldContainer, SampleContainer)
from pyphant.quantities.PhysicalQuantities import Quantity
from pyphant.core.KnowledgeManager import KnowledgeManager as KM
import numpy


class ParameterRun(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "ParameterRun"
    _params = [("pname", "Parameter name", "parameter", None),
               ("start", "Start", 0, None),
               ("stop", "Stop", 10, None),
               ("step", "Step", 1, None),
               ("unit", "Unit", "None", None)]
    _sockets = [("inputDC", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def createRun(self, inputDC, subscriber = 0):
        start = self.paramStart.value
        stop = self.paramStop.value
        step = self.paramStep.value
        pname = unicode(self.paramPname.value).encode('utf-8')
        unitstring = unicode(self.paramUnit.value).encode('utf-8')
        if unitstring != "None":
            unit = Quantity(unitstring)
        else:
            unit = 1
        paramData = numpy.arange(start, stop, step)
        paramFC = FieldContainer(paramData, unit=unit, longname=pname)
        emd5 = inputDC.id
        emd5FC = FieldContainer(
            numpy.array([emd5 for xr in xrange(paramData.shape[0])]),
            longname="emd5")
        km = KM.getInstance()
        km.registerDataContainer(inputDC)
        lname = "Parameter Run from %s to %s, step=%s, unit=%s"
        lname = lname % (start, stop, step, unitstring)
        emd5SC = SampleContainer([paramFC, emd5FC], longname=lname)
        emd5SC.seal()
        return emd5SC
