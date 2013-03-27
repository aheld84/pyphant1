# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
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
Pyphant module providing worker for finding the local extrema of 1D functions.
"""

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)
import OSC.OscAbsorption as OA
import scipy.interpolate
from pyphant import quantities
import copy

class ComputeFunctional(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Compute Functional"

    _sockets = [("field", Connectors.TYPE_ARRAY)]
    _params = [("extentX", u"Extension of x-axis [%%]", 10, None),
               ("extentY", u"Extension of y-axis [%%]", 10, None)]

    def computeDistances(self, field, subscriber=1, percentage=0):
        xGrid,yGrid = numpy.meshgrid(field.dimensions[-1].data,field.dimensions[-2].data)
        x    = numpy.extract(numpy.logical_not(numpy.isnan(field.data)),xGrid)
        xCon = DataContainer.FieldContainer(x,unit=field.dimensions[-1].unit,
                                            longname=field.dimensions[-1].longname,
                                            shortname=field.dimensions[-1].shortname)
        y    = numpy.extract(numpy.logical_not(numpy.isnan(field.data)),field.data)
        yCon = DataContainer.FieldContainer(y,longname=field.longname,
                                            shortname=field.shortname,
                                            unit=field.unit)
        xOff, xStep, xInd = OA.grid2Index(x, self.paramExtentX.value)
        yOff, yStep, yInd = OA.grid2Index(y, self.paramExtentY.value)

        xMax = xInd.maxV
        yMax = yInd.maxV
        xDim = DataContainer.FieldContainer( numpy.linspace(xInd.minV,xInd.maxV,xInd.stepCount), xCon.unit,
                                             longname = xCon.longname, shortname = xCon.shortname )
        yDim = DataContainer.FieldContainer( numpy.linspace(yInd.minV,yInd.maxV,yInd.stepCount), yCon.unit,
                                             longname = yCon.longname, shortname = yCon.shortname )
        functional = numpy.ones((xInd.stepCount, yInd.stepCount), dtype='float')
        distances = numpy.zeros(x.shape,'f')
        ni = functional.shape[0]
        nj = functional.shape[1]
        increment = 50.0/(ni*nj)
        for i in xrange(ni):
            for j in xrange(nj):
                for k in xrange(len(x)):
                    distances[k] = numpy.sqrt((x[k]-xDim.data[i])**2+
                                              (y[k]-yDim.data[j])**2)
                functional[i,j]=distances.min()
                percentage += increment
                subscriber %= percentage
        result = DataContainer.FieldContainer(functional.transpose(),
                                              dimensions=[yDim, xDim],
                                              longname = 'functional of %s'%field.longname,
                                              shortname= 'F_{%s}'%field.shortname
                                              )
        return result

    @Worker.plug(Connectors.TYPE_ARRAY)
    def compute(self, field, subscriber=1):
        percentage = 0
        functionals = DataContainer.SampleContainer([self.computeDistances(column, subscriber, percentage) for column in field],
                                                    longname='Functionals of %s'%field.longname,
                                                    shortname='F_{%s}'%field.shortname)
        functionals.seal()
        return functionals
