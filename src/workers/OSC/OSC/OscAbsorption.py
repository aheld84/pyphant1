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

import numpy
from pyphant.core import (Worker, Connectors, DataContainer)
from pyphant.quantities import Quantity
import logging
import pkg_resources


class IndexDict(object):
    def __init__(self, minV, maxV, step):
        self.minV = minV
        self.maxV = maxV
        self.step = step

    def __getitem__(self, key):
        return round((key - self.minV) / self.step)

    stepCount = property(lambda self:
                         round((self.maxV - self.minV) / self.step))


def grid2Index(field, extension=0):
    _logger = logging.getLogger("pyphant")
    f = numpy.unique(field)
    fmax = f.max()
    fmin = f.min()
    amplitude = fmax - fmin
    extent = extension / 200. * amplitude
    f.sort()
    fd = f[1:] - f[:-1]
    try:
        fstep = fd.min()
        offset = fmin - extent
        fmax += extent
    except ValueError:  # Occurs if all elements of array are equal
        fstep = f[0]
        offset = f[0] - extent
        fmax = f[0] + extent
    fic = (f - fmin) / fstep
    fi = fic.round().astype('int')
    if numpy.allclose(fi, fic):
        indexDict = IndexDict(offset, fmax, fstep)
    else:
        _logger.warning(u"There seems to be a problem with the discretisation.\
                            We are choosing 100 points.")
        fstep = (fmax - offset) / 100.
        indexDict = IndexDict(offset, fmax, fstep)
    return (offset, fstep, indexDict)


def removePeak(Abso, lower, upper):
    dim = Abso.dimensions[-1]
    minVal = lower / dim.unit
    maxVal = upper / dim.unit
    high_part = numpy.argwhere(minVal < dim.data).flatten()
    low_part = numpy.argwhere(dim.data < maxVal).flatten()
    lamp_interval = numpy.intersect1d(high_part, low_part)
    min_index = lamp_interval[0]
    max_index = lamp_interval[-1]
    steps = max_index - min_index
    for row in Abso.data:
        min_value = row[min_index]
        max_value = row[max_index]
        step_size = (max_value - min_value) / steps
        row[lamp_interval] = min_value + (lamp_interval - min_index) *\
                                    step_size


class OscAbsorptionCalculator(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant.osc").version
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
        A = - ((I.data - I_d.data) / (I_0.data - I_d.data) - 1)
        if self.paramClipping.value == 1:
            A[A > 1] = 1
            A[A < 0] = 0
        Abso = DataContainer.FieldContainer(A,
                                            longname=u'absorption',
                                            shortname=ur'\tilde{A}')
        Abso.dimensions[-1] = I.dimensions[-1]
        if self.paramMask_lamp.value == 1:
            removePeak(Abso, Quantity('654nm'), Quantity('660nm'))
            removePeak(Abso, Quantity('920nm'), Quantity('980nm'))
        Abso.seal()
        return Abso
