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
"""

__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)
import scipy.interpolate
from pyphant import quantities
import copy

class EstimateParameterFromValues(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Estimate Parameter from Values"

    _sockets = [("model", Connectors.TYPE_ARRAY),
                ("experimental", Connectors.TYPE_ARRAY)]
    _params = [("minima_model", u"Minima in the model", [u"Minima"], None),
               ("maxima_model", u"Maxima in the model", [u"Maxima"], None),
               ("minima_experimental", u"Minima in the experiment", [u"Minima"], None),
               ("maxima_experimental", u"Maxima in the experiment", [u"Maxima"], None),
               ("extentX", u"Extension of x-axis [%%]", 10, None),
               ("extentY", u"Extension of y-axis [%%]", 10, None)]

    def refreshParams(self, subscriber=None):
        if self.socketModel.isFull():
            templ = self.socketModel.getResult( subscriber )
            self.paramMinima_model.possibleValues = templ.longnames.keys()
            self.paramMaxima_model.possibleValues = templ.longnames.keys()
        if self.socketExperimental.isFull():
            templ = self.socketExperimental.getResult( subscriber )
            self.paramMinima_experimental.possibleValues = templ.longnames.keys()
            self.paramMaxima_experimental.possibleValues = templ.longnames.keys()

    @Worker.plug(Connectors.TYPE_IMAGE)
    def compute(self, model, experimental, subscriber=1):
        minima_model = model[self.paramMinima_model.value]
        maxima_model = model[self.paramMaxima_model.value]
        minima_experimental = experimental[self.paramMinima_experimental.value]
        minima_experimental = minima_experimental.inUnitsOf(minima_model)
        minima = minima_experimental.data.transpose()
        if minima_experimental.error != None:
            minima_error = iter(minima_experimental.error.transpose())
        else:
            minima_error = None
        maxima_experimental = experimental[self.paramMaxima_experimental.value]
        maxima_experimental = maxima_experimental.inUnitsOf(maxima_model)
        maxima = maxima_experimental.data.transpose()
        if maxima_experimental.error != None:
            maxima_error = iter(maxima_experimental.error.transpose())
        else:
            maxima_error = None
        parameter = []
        inc = 100.0/float(len(minima))
        acc = inc
        subscriber %= acc
        mask = []
        for row_minima, row_maxima in zip(minima, maxima):
            if minima_error:
                filtered_minima_error = filter(
                    lambda c: not numpy.isnan(c), minima_error.next())
            else:
                filtered_minima_error = None
            if maxima_error:
                filtered_maxima_error = filter(
                    lambda c: not numpy.isnan(c), maxima_error.next())
            else:
                filtered_maxima_error = None
            row_minima = numpy.array(filter(lambda c: not numpy.isnan(c), row_minima))
            row_maxima = numpy.array(filter(lambda c: not numpy.isnan(c), row_minima))
            grades = []
            for rm_minima, rm_maxima in zip(minima_model.data.transpose(), maxima_model.data.transpose()):
                rm_minima = filter(lambda c: not numpy.isnan(c), rm_minima)
                rm_maxima = filter(lambda c: not numpy.isnan(c), rm_maxima)
                grade = 0
                if len(rm_minima) == len(row_minima):
                    grade = sum(numpy.abs(numpy.array(rm_minima)-row_minima))
                if len(rm_maxima) == len(row_maxima):
                    grade += sum(numpy.abs(numpy.array(rm_maxima)-row_maxima))
                if grade == 0:
                    grades.append(numpy.nan)
                    continue
                grades.append(grade)
            grades = numpy.array(grades)
            i = numpy.nanargmin(grades)
            if numpy.isnan(i):
                mask.append(True)
                parameter.append(numpy.nan)
            else:
                mask.append(False)
                parameter.append(minima_model.dimensions[1].data[i])
            acc += inc
            subscriber %= acc
        result = DataContainer.FieldContainer(
            numpy.array(parameter),
            mask = numpy.array(mask),
            longname = minima_model.dimensions[-1].longname,
            shortname = minima_model.dimensions[-1].shortname,
            unit = minima_model.dimensions[-1].unit)
        result.seal()
        return result
