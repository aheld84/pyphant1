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
The Error Estimaotr Worker is a class of Pyphant's OSC-Toolbox. It
valuates the error caused by noise for every pixel in a field.
"""

__id__ = "$Id$"
__author__ = "$Author: obi $"
__version__ = "$Revision: 4276 $"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

from pyphant import quantities
import logging, copy, math
_logger = logging.getLogger("pyphant")

def localNoise( y, samples=50):
    length = len(y)
    samples2 = samples/2
    sampleM1 = samples-1
    sampleMod= samples%2
    #Initialize extended y-vector
    yExtended = numpy.zeros(length+samples-samples%2,'float')
    # Mirroring to the left
    yExtended[:samples2] = y[samples2:0:-1]
    # Copy of array
    yExtended[samples2:length+samples2] = y
    #Mirroring to the right
    yExtended[length+samples2:] = y[-2:-2-samples2:-1]
    #Inititalize error vector
    error = numpy.zeros(y.shape,'float')
    #Compute experimental standard deviation
    for i in xrange(samples2,length+samples2):
        sample = yExtended[i-samples2:i+samples2+sampleMod]
        yMean = numpy.mean(sample)
        error[i-samples2]=numpy.sqrt(numpy.sum((yMean-sample)**2)/sampleM1)
    return error

class ErrorEstimator(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision: 4276 $"[11:-1]
    name = "Estimate Error"

    _sockets = [("osc", Connectors.TYPE_IMAGE)]
    _params = [ ("dA", u"Window Size in number of data points", 10, None)
               ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def estimate(self, osc, subscriber=0):
        xCon = osc.data
        noise = numpy.zeros(xCon.shape,'float')
        intervallLength = self.paramDA.value
        count = xCon.shape[0]

        #Loop over all rows
        for i in xrange(count):
            x = xCon[i]
            noise[i] = localNoise(x, self.paramDA.value)
            subscriber %= float(i+1)/count*100.0

        result = copy.deepcopy(osc)
        result.error = noise
        result.seal()
        return result
