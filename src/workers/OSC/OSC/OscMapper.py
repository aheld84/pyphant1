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

import numpy
from pyphant.core import (Worker, Connectors, DataContainer)
from pyphant.quantities import Quantity
from OSC.OscAbsorption import grid2Index
import logging
import copy


class OscMapper(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Mapper"

    _sockets = [("osc", Connectors.TYPE_ARRAY)]
    _params = [("xAxis", u"x-Axis", [u"horizontal_table_position"], None),
               ("yAxis", u"y-Axis", [u"vertical_table_position"], None),
               ("field", u"Field", [u"thickness"], None),
               ("extentX", u"Extension of x-axis [%%]", 10, None),
               ("extentY", u"Extension of y-axis [%%]", 10, None),
               ("overrideV", u"Override value limits", False, None),
               ("vmin", u"Minimal value", "0 nm", None),
               ("vmax", u"Maximal value", "100 nm", None)]

    def inithook(self):
        self._logger = logging.getLogger("pyphant")

    def refreshParams(self, subscriber=None):
        if self.socketOsc.isFull():
            templ = self.socketOsc.getResult( subscriber )
            colNames = templ.longnames.keys()
            self.paramXAxis.possibleValues = colNames
            self.paramYAxis.possibleValues = colNames
            self.paramField.possibleValues = colNames

    def calcNormal(self, osc, xCon, yCon, fCon, xf, yf, h):
        xOff, xStep, xInd = grid2Index(xf, self.paramExtentX.value)
        yOff, yStep, yInd = grid2Index(yf, self.paramExtentY.value)
        xMax = xInd.maxV # never used!
        yMax = yInd.maxV # never used!
        xDim = DataContainer.FieldContainer(
            numpy.linspace(xInd.minV, xInd.maxV, xInd.stepCount) - 0.5 * xStep,
            xCon.unit,
            longname = xCon.longname,
            shortname = xCon.shortname
            )
        yDim = DataContainer.FieldContainer(
            numpy.linspace(yInd.minV, yInd.maxV, yInd.stepCount) - 0.5 * yStep,
            yCon.unit,
            longname = yCon.longname,
            shortname = yCon.shortname
            )
        img = numpy.ones((yInd.stepCount, xInd.stepCount),
                         dtype='float') * numpy.NaN
        mask = numpy.ones((yInd.stepCount, xInd.stepCount), dtype='bool')
        for i in xrange(xf.size):
            xi = xInd[xf[i]]
            yi = yInd[yf[i]]
            if not mask[yi, xi]:
                self._logger.warning("Duplicate data for pixel (%.4g,%.4g). "
                                     "Using first found value. "
                                     "Is your data corrupt?"%(xf[i],yf[i]))
            else:
                img[yi, xi] = h[i]
                if h[i] > 0:
                    mask[yi, xi] = False
        result = DataContainer.FieldContainer(
                                        img, fCon.unit, mask=mask,
                                        dimensions=[yDim, xDim],
                                        longname=u'Map of %s'%fCon.longname,
                                        shortname=fCon.shortname
                                        )
        return result

    @Worker.plug(Connectors.TYPE_IMAGE)
    def mapHeights(self, osc, subscriber=0):
        xCon = osc[self.paramXAxis.value]
        yCon = osc[self.paramYAxis.value]
        fCon = osc[self.paramField.value]
        cons = [copy.deepcopy(data) for data in [xCon, yCon, fCon]]
        xCon, yCon, fCon = cons
        for con in cons:
            con.longname = con.longname.replace('_', ' ')
            con.data = con.data.astype('float')
        xf, yf, h = tuple([con.data for con in cons])
        result = self.calcNormal(osc, xCon, yCon, fCon, xf, yf, h)
        if self.paramOverrideV.value:
            vs = str(self.paramVmin.value), str(self.paramVmax.value)
            try:
                vs = [Quantity(v) for v in vs]
            except SyntaxError:
                vs = [float(v) for v in vs]
            result.attributes['vmin'] = vs[0]
            result.attributes['vmax'] = vs[1]
        result.seal()
        return result
