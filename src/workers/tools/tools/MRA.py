# -*- coding: utf-8 -*-

# Copyright (c) 2008-2010, Rectorate of the University of Freiburg
# Copyright (c) 2009-2011  Andreas W. Liehr (liehr@users.sourceforge.net)
# Copyright (c) 2010, Klaus Zimmermann (zklaus@users.sourceforge.net)
# all rights reserved.
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
import logging, copy, math

from scipy.special import ive
from scipy.signal import convolve

def findMaxima(fieldData, numb_edge, lastExtrema=None):
    return findMinima(-fieldData,numb_edge, lastExtrema)

def findMinima(fieldData, numb_edge, lastExtrema=None):
    leftGreater = fieldData[:-2] >  fieldData[1:-1]
    leftEqual =   fieldData[:-2] == fieldData[1:-1]
    rightGreater =fieldData[1:-1] <  fieldData[2:] 
    rightEqual =  fieldData[2:] ==  fieldData[1:-1]
    minima_c = numpy.logical_and(leftGreater, rightGreater)                        # Minima
    minima_le = numpy.logical_and(leftGreater, rightEqual)                        
    minima_re = numpy.logical_and(rightGreater, leftEqual)
    minima_e = numpy.logical_and(minima_le[:-1], minima_re[1:])
    minima = 1 + numpy.logical_or(minima_c[:-1], minima_e).nonzero()[0]
    edge = len(fieldData)/numb_edge
    minima = minima[numpy.logical_or(edge<minima,minima<(len(fieldData)-edge))]
    if lastExtrema==None or len(minima)==0 or len(lastExtrema)==len(minima):
        return minima
    trackedMinima = []
    for lastMinimum in lastExtrema:
        distance = (minima-lastMinimum)**2
        trackedMinima.append(distance.argmin())
    result = minima[trackedMinima]
    return result

def convolveMRA(field, sigma):
    if sigma==0:
        return field.data
    n = int(len(field.dimensions[-1].data)/2)
    kernel = ive(numpy.arange(-n, n), sigma)
    return convolve(field.data, kernel, mode='same')

class MraError(RuntimeError):
    def __init__(self, msg, convolvedField):
        RuntimeError.__init__(self, msg)
        self.convolvedField = convolvedField

def mra1d(dim, field, n, numb_edge):
    sigmaSpace = numpy.linspace(n, 0, 10)
    convolvedField = convolveMRA(field, sigmaSpace[0])
    firstMinima = lastMinima = findMinima(convolvedField, numb_edge, None)
    firstMaxima = lastMaxima = findMaxima(convolvedField, numb_edge, None)
    if len(firstMinima)==0 and len(firstMaxima)==0:
        raise MraError("No Extrema found at sigma level %s"%sigmaSpace[0],
                       convolvedField)
    for sigma in sigmaSpace[1:]:
        convolvedField = convolveMRA(field, sigma)
        lastMinima = findMinima(convolvedField, numb_edge, lastMinima)
        lastMaxima = findMaxima(convolvedField, numb_edge, lastMaxima)
    if len(lastMinima)>0 and len(firstMinima)>0:
        pos_minima = dim.data[numpy.array(lastMinima)]
        error_minima = numpy.abs(pos_minima - dim.data[numpy.array(firstMinima)])
    else:
        pos_minima = numpy.array([],dtype=dim.data.dtype)
        error_minima = numpy.array([],dtype=dim.data.dtype)
    if len(lastMaxima)>0 and len(firstMaxima)>0:
        pos_maxima = dim.data[numpy.array(lastMaxima)]
        error_maxima = numpy.abs(pos_maxima - dim.data[numpy.array(firstMaxima)])
    else:
        pos_maxima = numpy.array([],dtype=dim.data.dtype)
        error_maxima = numpy.array([],dtype=dim.data.dtype)
    result = ((pos_minima, error_minima), (pos_maxima, error_maxima))
    return result

def pos_error_to_data_container(p_e):
    n = max(map(lambda (p,e): len(p), p_e))
    m = len(p_e)
    pos = numpy.ones((m,n),'float')*numpy.NaN
    error = pos.copy()
    for i in xrange(m):
        for j in xrange(len(p_e[i][0])):
            pos[i,j] = p_e[i][0][j]
            error[i,j] = p_e[i][1][j]
    return n, pos, error

class MRA(Worker.Worker):
    API = 2
    VERSION = 2
    REVISION = "$Revision$"[11:-1]
    name = "Multi Resolution Analyzer"

    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("scale", u"Scale", "200 nm", None),
               ("numb_edge", u"Width of edge to discard extrema in [%%]", 5, None),
               ("longname",u"Name of result",'default',None),
               ("symbol",u"Symbol of result",'default',None)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def mra(self, field, subscriber=0):
        dim = field.dimensions[-1]
        try:
            scale = quantities.Quantity(self.paramScale.value.encode('utf-8'))
        except:
            scale = float(self.paramScale.value)
        numb_edge = 100.0/self.paramNumb_edge.value
        d = scipy.diff(dim.data)
        numpy.testing.assert_array_almost_equal(d.min(), d.max(),4)
        sigmaMax = scale/(d[0]*dim.unit)
        if len(field.data.shape)>1:
            p_e = []
            inc = 100./len(field.data)
            acc = 0.
            for field1d in field:
                try:
                    p_e.append(mra1d(dim, field1d, sigmaMax, numb_edge))
                except MraError:
                    p_e.append((([],[]),([],[])))
                acc += inc
                subscriber %= acc
            minima, maxima = zip(*p_e)
            n_min, pos_min, err_min = pos_error_to_data_container(minima)
            n_max, pos_max, err_max = pos_error_to_data_container(maxima)
            dims_min = [DataContainer.generateIndex(0,n_min), field.dimensions[0]]
            dims_max = [DataContainer.generateIndex(0,n_max), field.dimensions[0]]
        else:
            (pos_min, err_min), (pos_max, err_max) = mra1d(dim, field, sigmaMax, numb_edge)
            dims_min = [DataContainer.generateIndex(0,len(pos_min))]
            dims_max = [DataContainer.generateIndex(0,len(pos_max))]
            subscriber %= 100.
        minima = DataContainer.FieldContainer(pos_min.transpose(),
                                              error = err_min.transpose(),
                                              unit = dim.unit,
                                              dimensions = dims_min,
                                              mask = numpy.isnan(pos_min).transpose(),
                                              longname="%s of the local %s of %s" % (dim.longname,"minima",field.longname),
                                              shortname="%s_{min}" % dim.shortname)
        maxima = DataContainer.FieldContainer(pos_max.transpose(),
                                              error = err_max.transpose(),
                                              unit = dim.unit,
                                              dimensions = dims_max,
                                              mask = numpy.isnan(pos_max).transpose(),
                                              longname="%s of the local %s of %s" % (dim.longname,"maxima",field.longname),
                                              shortname="%s_{max}" % dim.shortname)
        roots = DataContainer.SampleContainer([minima, maxima],
                                               longname="%s of the local %s of %s" % (dim.longname,"extrema",field.longname),
                                               shortname="%s_{extrem}" % dim.shortname)
        if self.paramLongname.value != 'default':
            roots.longname = self.paramLongname.value
        if self.paramSymbol.value != 'default':
            roots.shortname = self.paramSymbol.value
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
