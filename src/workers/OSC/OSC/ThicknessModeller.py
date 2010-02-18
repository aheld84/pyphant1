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
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)
import OSC.OscAbsorption
import scipy.interpolate
from pyphant import quantities
import logging, copy, math

class ThicknessModeller(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Coat Thickness Model"

    _sockets = [("osc", Connectors.TYPE_ARRAY)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calcAbsorption(self, osc, subscriber=0):
        A = copy.deepcopy(osc[u'absorption'])
        heights = osc[u'thickness']
        indexMap = dict([(h,i) for i,h in enumerate(heights.data)])
        h = copy.deepcopy(heights.data)
        h.sort()
        data = numpy.vstack([ copy.deepcopy(A.data[indexMap[i]]) for i in h ])
        height = copy.deepcopy(heights)
        height.data = h
        attr = copy.deepcopy(A.attributes).update(osc.attributes)
        result = DataContainer.FieldContainer(data,unit=A.unit,
                                              longname=A.longname,
                                              shortname=A.shortname,
                                              attributes=attr,
                                              dimensions=[height, A.dimensions[-1]])
        result.seal()
        return result


class ThicknessSmoother(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Coat Thickness Smoother"

    _sockets = [("osc", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calcSmoother(self, osc, subscriber=0):
        x,y = copy.deepcopy(osc.dimensions[0].data),copy.deepcopy(osc.dimensions[1].data)
        X,Y = scipy.meshgrid(x,y)
        Z = osc.data#scipy.diff(osc.data,2,0)
        spline = scipy.interpolate.interp2d(X.flatten(),Y.flatten(),Z.flatten())
        X,Y = scipy.meshgrid(numpy.linspace(x.min(), x.max(), 10),
                             numpy.linspace(y.min(), y.max(), 10))
        Z = spline(X.flatten(),Y.flatten())
        Z.resize((10,10))
        result = DataContainer.FieldContainer(Z,dimensions=osc.dimensions)
        result.seal()
        return result
