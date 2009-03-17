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
import logging, copy, math

from scipy.special import ive
from scipy.signal import convolve

def findMinima(fieldData, lastExtrema=None):
    leftGreater = fieldData[:-2] > fieldData[1:-1]
    leftEqual = fieldData[:-2] == fieldData[1:-1]
    rightGreater = fieldData[2:] > fieldData[1:-1]
    rightEqual = fieldData[2:] == fieldData[1:-1]

    minima_c = numpy.logical_and(leftGreater, rightGreater)
    minima_le = numpy.logical_and(leftGreater, rightEqual)
    minima_re = numpy.logical_and(rightGreater, leftEqual)
    minima_e = numpy.logical_and(minima_le[:-1], minima_re[1:])
    minima = numpy.logical_or(minima_c[1:], minima_e).nonzero()[0]
    if lastExtrema==None or len(minima)==0 or len(lastExtrema)==len(minima):
        return minima
    trackedMinima = []
    for lastMinimum in lastExtrema:
        distance = (minima-lastMinimum)**2
        trackedMinima.append(distance.argmin())
    return minima[trackedMinima]

def convolveMRA(field, sigma):
    if sigma==0:
        return field.data
    n = int(len(field.dimensions[-1].data)/2)
    kernel = ive(numpy.arange(-n, n), sigma)
    return convolve(field.data, kernel, mode='same')

#def mra1d(dim, field, n):
#    mrr = [convolveMRA(field, sigma) for sigma in
#           numpy.linspace(1, n,10).tolist()]
#    mrr.insert(0,field.data)
#    firstMinima = lastMinima = findMinima(mrr[-1], None)
#    for row in reversed(mrr[:-1]):
#        lastMinima = findMinima(row, lastMinima)
#    pos = dim.data[numpy.array(lastMinima)+1]
#    error = numpy.abs(pos - dim.data[numpy.array(firstMinima)+1])
#    return pos, error

class MraError(RuntimeError):
    def __init__(self, msg, convolvedField):
        RuntimeError.__init__(self, msg)
        self.convolvedField = convolvedField

def mra1d(dim, field, n):
    sigmaSpace = numpy.linspace(n, 1, 10)
    convolvedField = convolveMRA(field, sigmaSpace[0])
    firstMinima = lastMinima = findMinima(convolvedField, None)
    if len(firstMinima)==0:
        raise MraError("No Minima found at sigma level %s"%sigmaSpace[0],
                       convolvedField)
    for sigma in sigmaSpace[1:]:
        convolvedField = convolveMRA(field, sigma)
        lastMinima = findMinima(convolvedField, lastMinima)
        if len(lastMinima)==0:
            import pylab
            pylab.plot(convolvedField)
            pylab.show()
    pos = dim.data[numpy.array(lastMinima)+1]
    error = numpy.abs(pos - dim.data[numpy.array(firstMinima)+1])
    return pos, error


class MRA(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Multi Resolution Analyser"

    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("scale", u"Scale", "200 nm", None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def mra(self, field, subscriber=0):
        dim = field.dimensions[-1]
        try:
            scale = PhysicalQuantities.PhysicalQuantity(self.paramScale.value.encode('utf-8'))
        except:
            scale = float(self.paramScale.value)
        d = scipy.diff(dim.data)
        numpy.testing.assert_array_almost_equal(d.min(), d.max(),4)
        sigmaMax = scale/(d[0]*dim.unit)
        if len(field.data.shape)>1:
            p_e = []
            inc = 100./len(field.data)
            acc = 0.
            for field1d in field:
                try:
                    p_e.append(mra1d(dim, field1d, sigmaMax))
                except MraError:
                    p_e.append(([],[]))
                acc += inc
                subscriber %= acc
            n = max(map(lambda (p,e): len(p), p_e))
            m = len(p_e)
            pos = numpy.ones((m,n),'float')*numpy.NaN
            error = pos.copy()
            for i in xrange(m):
                for j in xrange(len(p_e[i][0])):
                    pos[i,j] = p_e[i][0][j]
                    error[i,j] = p_e[i][1][j]
            dims = [DataContainer.generateIndex(0,n), field.dimensions[0]]
        else:
            pos, error = mra1d(dim, field, sigmaMax)
            n = len(pos)
            dims = [DataContainer.generateIndex(0,n)]
            subscriber %= 100.
        roots = DataContainer.FieldContainer(pos.transpose(),
                                             error = error.transpose(),
                                             unit = dim.unit,
                                             dimensions = dims,
                                             mask = numpy.isnan(pos).transpose(),
                                             longname="%s of the local %s of %s" % (dim.longname,"minima",field.longname),
                                             shortname="%s_0" % dim.shortname)
        roots.seal()
        return roots

def main():
    import pylab
    mra = MRA()
    N=200
    x = numpy.linspace(-2, 2, N)
    y = x**4-3*x**2+x
    z = y + scipy.random.randn(N)*0.5
    data = DataContainer.FieldContainer(z, dimensions=[DataContainer.FieldContainer(x, unit='1m')])
    mra.paramScale.value = "1.0m"
    roots = mra.mra(data)
    pylab.plot(x,y,x,z)
    pylab.vlines(roots.data, -4, 4)
    pylab.vlines(roots.data+roots.error, -4, 4, linestyle='dashed')
    pylab.vlines(roots.data-roots.error, -4, 4, linestyle='dashed')
    pylab.show()

if __name__ == '__main__':
    main()
