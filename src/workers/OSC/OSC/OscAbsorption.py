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

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

import scipy.interpolate
from pyphant import quantities
import logging, copy, math

def grid2Index(field, extension=0):
    _logger = logging.getLogger("pyphant")
    f = numpy.unique(field)
    fmax = f.max()
    fmin = f.min()
    amplitude = fmax-fmin
    extent = extension/200.*amplitude
    f.sort()
    fd = f[1:]-f[:-1]
    try:
        fstep = fd.min()
        offset = fmin-extent
        fmax += extent
    except ValueError, e: #Occurs if all elements of array are equal
        fstep = f[0]
        offset = f[0] - extent
        fmax = f[0] + extent
    fic = (f-fmin)/fstep
    fi = fic.round().astype('int')
    if numpy.allclose(fi,fic):
        indexDict = IndexDict(offset, fmax, fstep)
    else:
        _logger.warning(u"There seems to be a problem with the discretisation. We are chosing 100 points.")
        fstep = (fmax-offset)/100.
        indexDict = IndexDict(offset,fmax,fstep)
    return (offset, fstep, indexDict)

def removePeak(Abso, lower, upper):
    dim = Abso.dimensions[-1]
    minVal = lower/dim.unit
    maxVal = upper/dim.unit
    high_part = numpy.argwhere(minVal<dim.data).flatten()
    low_part = numpy.argwhere(dim.data<maxVal).flatten()
    lamp_interval = numpy.intersect1d(high_part, low_part)
    min_index = lamp_interval[0]
    max_index = lamp_interval[-1]
    steps = max_index-min_index
    for row in Abso.data:
        min_value = row[min_index]
        max_value = row[max_index]
        step_size = (max_value-min_value)/steps
        row[lamp_interval] = min_value + (lamp_interval-min_index)*step_size

class OscAbsorptionCalculator(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Compute Absorption"

    _sockets = [("osc", Connectors.TYPE_ARRAY)]
    _params = [("clipping", "Clipping", 1, None),
               ("mask_lamp", "Mask lamp", 0, None)]

    def inithook(self):
        self._logger = logging.getLogger("pyphant")

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calcAbsorption(self, osc, subscriber=0):
        I = osc[u'I']
        I_d = osc[u'I_d']
        I_0 = osc[u'I_0']
        A = -((I.data-I_d.data)/(I_0.data-I_d.data)-1)
        if self.paramClipping.value==1:
            A[A>1] = 1
            A[A<0] = 0
        Abso = DataContainer.FieldContainer(A,
                                            longname=u'absorption',
                                            shortname=ur'\tilde{A}')
        Abso.dimensions[-1] = I.dimensions[-1]
        if self.paramMask_lamp.value==1:
            removePeak(Abso,
                       quantities.Quantity('654nm'),
                       quantities.Quantity('660nm'))
            removePeak(Abso,
                       quantities.Quantity('920nm'),
                       quantities.Quantity('980nm'))
        Abso.seal()
        return Abso


class ColumnExtractor(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Column Extractor"

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
            result = DataContainer.FieldContainer( data.data, mask=data.mask,
                                                   unit = col.unit,
                                                   dimensions = [dim],
                                                   longname=col.longname,
                                                   shortname=col.shortname)
        #result.attributes = osc.attributes
        result.attributes = col.attributes
        result.seal()
        return result

class IndexDict(object):
    def __init__(self, minV, maxV, step):
        self.minV = minV
        self.maxV = maxV
        self.step = step
    def __getitem__(self, key):
        return round((key-self.minV)/self.step)
    stepCount = property(lambda self: round((self.maxV-self.minV)/self.step))


class OscMapper(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Osc Mapper"

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
        xMax = xInd.maxV
        yMax = yInd.maxV
        xDim = DataContainer.FieldContainer(
            numpy.linspace(xInd.minV,xInd.maxV,xInd.stepCount)-0.5*xStep,
            xCon.unit,
            longname = xCon.longname, shortname = xCon.shortname )
        yDim = DataContainer.FieldContainer(
            numpy.linspace(yInd.minV,yInd.maxV,yInd.stepCount)-0.5*yStep,
            yCon.unit,
            longname = yCon.longname, shortname = yCon.shortname )
        img = numpy.ones((yInd.stepCount, xInd.stepCount),
                         dtype='float')*numpy.NaN
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
                if h[i]>0:
                    mask[yi, xi] = False
        result = DataContainer.FieldContainer(
            img, fCon.unit, mask=mask, dimensions=[yDim, xDim],
            longname=u'Map of %s'%fCon.longname, shortname=fCon.shortname)
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
        xf, yf, h = tuple([ con.data for con in cons ])
        result = self.calcNormal(osc, xCon, yCon, fCon, xf, yf, h)
        if self.paramOverrideV.value:
            vs = str(self.paramVmin.value), str(self.paramVmax.value)
            from pyphant.quantities import (
                isQuantity, Quantity)
            try:
                vs = [Quantity(v) for v in vs]
            except SyntaxError:
                vs = [float(v) for v in vs]
            result.attributes['vmin'] = vs[0]
            result.attributes['vmax'] = vs[1]
        result.seal()
        return result
