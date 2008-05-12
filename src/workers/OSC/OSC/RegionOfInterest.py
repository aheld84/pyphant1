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

u"""
"""

__id__ = "$Id$"
__author__ = "$Author: obi $"
__version__ = "$Revision: 4276 $"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

from Scientific.Physics import PhysicalQuantities
import logging, copy, math
_logger = logging.getLogger("pyphant")


class RegionOfInterest(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision: 4276 $"[11:-1]
    name = "Region of Interest"

    _sockets = [("osc", Connectors.TYPE_IMAGE)]
    _params = [ ("start", u"intervall start", "300nm", None),
               ("stop", u"intervall stop", "800nm", None)
               ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def prune(self, osc, subscriber=0):
        yCon = copy.deepcopy(osc)
        xCon = copy.deepcopy(osc.dimensions[-1])

        def rescaleUnit(quantityParam):
            if PhysicalQuantities.isPhysicalQuantity(xCon.unit):
                try:
                    quantity = PhysicalQuantities.PhysicalQuantity(quantityParam.value.encode('utf-8'))
                    print quantity
                    return quantity.inUnitsOf(xCon.unit.unit).value
                except:
                    raise TypeError, 'Unit %s cannot be expressed in units of %s.' % (quantityParam.value,xCon.unit)
            else:
               try:
                   quantity = float(quantityParam.value.encode('utf-8'))
                   return quantity/xCon.unit
               except:
                    raise TypeError, 'Unit %s cannot be expressed in units of %s.' % (quantityParam.value,xCon.unit)

        start,stop = map(rescaleUnit,[self.paramStart,self.paramStop])

        x = xCon.data
        index = numpy.logical_and(x >= start,x<=stop)
        newX = numpy.extract(index, x)
        newXCon = DataContainer.FieldContainer(numpy.array(newX),
                                               longname=xCon.longname,
                                               shortname=xCon.shortname,
                                               unit=xCon.unit)
        if len(yCon.data.shape)==2:
            yIndex = numpy.repeat(index[numpy.newaxis,:], yCon.data.shape[0], 0)
            yd = yCon.data.shape[0]
        else:
            yIndex = index
            yd = 1
        xd = newXCon.data.shape[0]
        newY = numpy.extract(yIndex, yCon.data).reshape(yd, xd)
        if yCon.error != None:
            newError = numpy.extract(yIndex, yCon.error).reshape(yd, xd)
        else:
            newError = None
        if yCon.mask != None:
            newMask = numpy.extract(yIndex, yCon.mask).reshape(yd, xd)
        else:
            newMask = None
        if len(yCon.data.shape)==1:
            if newError !=None:
                newError = newError.squeeze()
            if newMask !=None:
                newMask = newMask.squeeze()
            result = DataContainer.FieldContainer(newY.squeeze(),
                                                  error=newError,
                                                  mask=newMask,
                                                  dimensions=[newXCon],
                                                  longname=yCon.longname,
                                                  shortname=yCon.shortname,
                                                  unit=yCon.unit,rescale=True)
        else:
            result = DataContainer.FieldContainer(newY,
                                                  error=newError,
                                                  mask=newMask,
                                                  dimensions=[yCon.dimensions[0], newXCon],
                                                  longname=yCon.longname,
                                                  shortname=yCon.shortname,
                                                  unit=yCon.unit,rescale=True)
        result.seal()
        return result
