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
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

import scipy.interpolate
from pyphant.quantities import Quantity
import logging, copy, math

class OscThicknessCorrector(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Correct Thickness"

    _sockets = [("osc", Connectors.TYPE_ARRAY)]
    _params = [("method","Correct thickness for", ["Spin Coating", "Printing"], None),
               ("max_correction", "Max correction", "30 nm", None)]


    def inithook(self):
        self._logger = logging.getLogger("pyphant")

    def perform_spincoat_correction(self, x, y, uncorrected_t):
        t = copy.deepcopy(uncorrected_t)
        r = numpy.sqrt(x.data**2+y.data**2)
        r_min = r.min()
        r_max = r.max()
        correction = Quantity(self.paramMax_correction.value)/t.unit
        t.data = t.data + correction*((r-r_min)/(r_max-r_min))
        t.longname='thickness corrected for spin coating'
        t.shortname='t_c'
        return t

    def perform_print_correction(self, x, raw_y, uncorrected_t):
        t = copy.deepcopy(uncorrected_t)
        y = raw_y.data
        d = 1.9*y**2 + 19.3*y + 49
        t.data = t.data - d
        t.longname='thickness corrected for printing'
        t.shortname='t_c'
        return t

    @Worker.plug(Connectors.TYPE_IMAGE)
    def correct(self, osc, subscriber=0):
        x = osc[u'x-position']
        y = osc[u'y-position']
        t = osc[u'thickness']
        method = self.paramMethod.value
        if  method == "Spin Coating":
            corrected_t = self.perform_spincoat_correction(x, y, t)
        elif method == "Printing":
            corrected_t = self.perform_print_correction(x, y, t)
        else:
            raise RuntimeError, "Unknown correction method %s." % method
        corrected_t.seal()
        return corrected_t
