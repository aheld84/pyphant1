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
from Scientific.Physics import PhysicalQuantities
import logging, copy, math

from scipy.special import ive
from scipy.signal import convolve

class MRA(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Multi Resolution Analyser"

    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("scale", u"Scale", "50 nm", None)]

    def convolve(self, field, sigma):
        if sigma==0:
            return field.data
        n = int(len(field.dimensions[-1].data)/2)
        kernel = ive(numpy.arange(-n, n), sigma)
        return convolve(field.data, kernel, mode='same')
        
    def findMinima(self, fieldData, lastExtrema=None):
        minima_c = numpy.logical_and(fieldData[:-2] > fieldData[1:-1],
                                   fieldData[2:]  > fieldData[1:-1])
        minima = minima_c.nonzero()[0]
        if lastExtrema==None:
            return minima
        trackedMinima = []
        for lastMinimum in lastExtrema:
            distance = (minima-lastMinimum)**2
            trackedMinima.append(distance.argmin())
        return minima[trackedMinima]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def mra(self, field, subscriber=0):
        dim = field.dimensions[-1]
        try:
            scale = PhysicalQuantities.PhysicalQuantity(self.paramScale.value)
        except:
            scale = float(self.paramScale.value)
        d = scipy.diff(dim.data)
        assert numpy.allclose(d.min(), d.max())
        n = scale/d[0]*dim.unit
        mrr = [self.convolve(field, sigma) for sigma in
               numpy.linspace(1, n,100).tolist()]
        lastMinima = None
        origExtremaPos = None
        for row in mrr.__reversed__():
            newMinima = self.findMinima(row, lastMinima)
            lastMinima = newMinima
            print dim.data[numpy.array(newMinima)]
            #origExtremaPos = newOrigExtremaPos
        roots = DataContainer.FieldContainer(dim.data[numpy.array(newMinima)],
                                             unit = dim.unit,
                                             longname="%s of the local %s of %s" % (dim.longname,"minima",field.longname),
                                             shortname="%s_0" % dim.shortname)
        roots.seal()
        return mrr, roots

def main():
    import pylab
    mra = MRA()
    x = numpy.linspace(-2, 2, 100)
    y = x**4-3*x**2+x
    #z = y + scipy.random.randn(100)*0.5
    z = numpy.array([ 2.34780571,  2.09156238,  0.5332234 , -0.02834118, -0.32603188,
                      -0.60151411, -1.11347491, -2.08409331, -2.70819461, -3.18515954,
                      -3.05347274, -3.34044027, -2.13135733, -4.01050254, -3.41987657,
                      -3.6012123 , -3.78173869, -3.47931019, -3.24799948, -3.11049149,
                      -3.5452045 , -3.06428498, -3.21358035, -2.96396225, -3.62057493,
                      -2.72119203, -2.66721085, -2.82274751, -3.77335446, -2.69488486,
                      -2.01602774, -1.68001615, -1.52803751, -2.82155386, -1.87232676,
                      -1.4543144 , -0.81421548, -0.67173508, -0.67432948, -1.62994539,
                      -0.70960285, -0.59510169, -0.77448565, -0.61368053, -0.46649733,
                      1.24964375, -0.13614141, -0.47720227,  0.56392326,  0.76611274,
                      0.09380934,  0.06581185,  0.8145737 , -0.51146898, -0.41842572,
                      0.5122507 , -0.28047205,  0.99774688,  0.29451745,  0.47395212,
                      0.24947649, -0.52780659, -0.87432683, -0.45071175,  0.13419426,
                      -0.99334888, -0.19878416, -0.11586503, -0.03590624, -1.02419055,
                      -0.12816827, -0.59284413, -1.83761451, -1.61972556, -0.56452747,
                      -0.97584479, -0.69704826, -1.34867496, -0.48626359,  0.19873513,
                      -1.25647259, -0.06859142, -1.44884286, -1.13005531, -1.28660869,
                      -0.97218543, -0.58118687,  0.28563569, -0.31884048,  0.74143098,
                      0.35096262,  1.71650232,  0.77247154,  2.35576553,  2.61386751,
                      2.75560072,  3.11663764,  5.81077989,  6.06092933,  6.08185724])
    data = DataContainer.FieldContainer(z, dimensions=[DataContainer.FieldContainer(x)])
    #c = mra.convolve(data, 10)
    #pylab.plot(x, c)
    mra.paramScale.value = "2"
    mrr, roots = mra.mra(data)
    pylab.plot(x, mrr[-1])
    for c in mrr:
        pylab.plot(x, c)
        pylab.plot(x, y)
        pylab.plot(x, z)
    mrr.append(y)
    pylab.vlines(roots.data, -4, 4)
    #pylab.matshow(numpy.array(mrr))
    #pylab.vlines(roots.data, 0, len(mrr)-1)
    pylab.show()

if __name__ == '__main__':
    main()
