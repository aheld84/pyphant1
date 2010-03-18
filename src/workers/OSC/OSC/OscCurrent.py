# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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
import copy, logging
_logger = logging.getLogger("pyphant")


def createModel(model):
    xData = model.data[u'\\Psi_{3}'].tolist()[0]
    yData = model.data[u'\\Psi_{1}'].tolist()[0]
    return scipy.interpolate.interp1d(xData,yData,
                                      kind='linear',
                                      bounds_error=False,
                                      fill_value=0.0)

class OscThickness2CurrentDensity(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Convert Thickness to Current Density"

    _sockets = [("osc", Connectors.TYPE_IMAGE),
                ("model", Connectors.TYPE_ARRAY)]
    _params = [("diameter", u"Diameter of probing area (eg. 800mum)", 'unknown', None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calcCurrentDensity(self, osc, model, subscriber=0):
        #Compute conversion factor between units
        #{u'\\Psi_{1}': Quantity(1.0,'mA/cm**2'),
        # u'\\Psi_{2}': 1.0, u'\\Psi_{3}': Quantity(1.0,'nm'),
        # u'\\Psi_{4}': 1.0, u'\\Psi_{0}': 1.0}
        unit = model._units[u'\\Psi_{3}']
        inputUnit = osc.unit
        assert inputUnit.isCompatible(unit.unit),'Units of input and output data are not compatible.'
        factor = inputUnit.inUnitsOf(unit.unit).value
        #Get model
        modelOperator = createModel(model)
        #Apply model
        inputData = factor * osc.data
        resultData = modelOperator(inputData)
        if resultData.min() == 0 and resultData.max() == 0:
            _logger.warning("The model does not describe the considered data.")
        #Incorporate area of probe
        if self.paramDiameter.value == 'unknown':
            factor = 1.0
        else:
            diameter = quantities.Quantity(self.paramDiameter.value.encode('latin-1'))
            factor = 0.25 * numpy.pi * diameter**2

        scaledUnit = factor * model._units[u'\\Psi_{1}']
        #Build Fieldcontainer
        result = DataContainer.FieldContainer(resultData,
                                              mask = osc.mask,
                                              longname=u'maximal short current density',
                                              shortname=u'\sigma',
                                              unit=scaledUnit,rescale=True,
                                              dimensions=copy.deepcopy(osc.dimensions))
        result.seal()
        return result
