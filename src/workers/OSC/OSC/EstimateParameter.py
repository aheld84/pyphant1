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
import scipy.interpolate
from pyphant.quantities import PhysicalQuantities
import copy


class EstimateParameter(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Estimate Parameter"

    _sockets = [("model", Connectors.TYPE_IMAGE),
                ("experimental", Connectors.TYPE_IMAGE)]
    _params = [("extentX", u"Extension of x-axis [%%]", 10, None),
               ("extentY", u"Extension of y-axis [%%]", 10, None)]

    def calculateThickness(self, row, model,error=None):
        if len(row)==0:
            return numpy.nan
        data = model.data.transpose()
        def calc(row, col,error):
            if error:
                return sum([col[numpy.argmin(((model.dimensions[0].data-c)/e)**2)]
                            for c,e in zip(row,error)])
            else:
                return sum([col[numpy.argmin((model.dimensions[0].data-c)**2)]
                            for c in row])
        i = numpy.argmin(numpy.array([calc(row, col,error) for col in data]))
        return model.dimensions[1].data[i]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def compute(self, model, experimental, subscriber=1):
        renormedExp = experimental.inUnitsOf(model.dimensions[0])
        minima = renormedExp.data.transpose()
        if renormedExp.error != None:
            error = iter(renormedExp.error.transpose())
        else:
            error = None
        parameter = []
        inc = 100.0/float(len(minima))
        acc = inc
        subscriber %= acc
        for row in minima:
            if error:
                filteredError = filter(lambda c: not numpy.isnan(c), error.next())
            else:
                filteredError = None
            parameter.append(self.calculateThickness( filter(lambda c: not numpy.isnan(c), row),
                                                      model,
                                                      filteredError))
            acc += inc
            subscriber %= acc
        result = DataContainer.FieldContainer(numpy.array(parameter),
                                              longname = model.dimensions[-1].longname,
                                              shortname = model.dimensions[-1].shortname,
                                              unit = model.dimensions[-1].unit)
        result.seal()
        return result
