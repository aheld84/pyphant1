# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008, Rectorate of the University of Freiburg
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
The Smoother Worker is a class of Pyphant's OSC Toolbox. It is used to
reduce noise from a field. The numer of smoothing runs can be edited.
"""

__author__ = "$Author: obi $"
__version__ = "$Revision: 4276 $"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

import scipy.interpolate
from pyphant import quantities
import logging, copy, math
_logger = logging.getLogger("pyphant")

class Smoother(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision: 4276 $"[11:-1]
    name = "Smoother"

    _sockets = [("osc", Connectors.TYPE_IMAGE)]
    _params = [("smoothing", "Fit smoothing (0 no smoothing, larger value more smoothing)", "1", None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def smooth(self, osc, subscriber=0):
        s = float(self.paramSmoothing.value)
        xDim = osc.dimensions[-1]
        x = xDim.data
        smoothedData = []
        count = osc.data.shape[0]
        for i in xrange(count):
            y = osc.data[i]
            if osc.error != None:
                error = copy.deepcopy(osc.error[i])
                error[error==0] = numpy.finfo(type(0.3)).eps
                weights = 1.0/(error**2)
                smoothYTCK,fp,ier,msg = scipy.interpolate.splrep(x,y,w=weights,s=s,
                                                                 full_output=True,task=0)
            else:
                smoothYTCK,fp,ier,msg = scipy.interpolate.splrep(x,y,s=s,
                                                                 full_output=True,task=0)
            if ier>0:
                _logger.warning("There was a problem in fitting: %i: %s, fp: %f" %(ier, msg, fp))
            smoothY = scipy.interpolate.splev(x,smoothYTCK)
            smoothedData.append(smoothY)
            subscriber %= float(i)*100.0/float(count)
        sya = numpy.array(smoothedData)
        result = DataContainer.FieldContainer(sya,
                                             error = osc.error,
                                             unit=osc.unit,
                                             dimensions = osc.dimensions,
                                             longname=u'Smoothed %s'%osc.longname,
                                             shortname='\\widetilde{%s}'%osc.shortname)
        result.seal()
        return result
