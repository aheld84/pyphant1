# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer

import ImageProcessing

import numpy, copy, pylab
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity as PQ

def unit(value):
    try:
        uObj = float(value)
    except ValueError:
        uObj = PQ(value)
    return uObj

class SlopeCalculator(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "SlopeCalculator"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = []

    @Worker.plug(Connectors.TYPE_IMAGE)
    def slope(self, image, subscriber=0):
        assert image.dimensions[0].unit == image.dimensions[1].unit, "Units of both dimensions have to be equal."

        newShape = [dim+2 for dim in image.data.shape]
        paddedField=numpy.zeros(newShape,image.data.dtype)
        paddedField[1:-1,1:-1] = image.data
        paddedField[0,:]  = paddedField[1,:]
        paddedField[-1,:] = paddedField[-2,:]
        paddedField[:,0]  = paddedField[:,1]
        paddedField[:,-1] = paddedField[:,-2]

        dx     = numpy.diff(image.dimensions[0].data)
        dy     = numpy.diff(image.dimensions[1].data)
        if dx.min() == dx.max() and dy.min() == dy.max():
            print "Calculating gradients with O(2)."
            NablaX = 0.5*(paddedField[:,:-2]-paddedField[:,2:])/dx.min()
            NablaY = 0.5*(paddedField[:-2,:]-paddedField[2:,:])/dy.min()
            xAbs = NablaX[1:-1,:]**2
            yAbs = NablaY[:,1:-1]**2
        else:
            print "Calculating (right-side) gradient with O(1)."
            NablaX = numpy.diff(paddedField,axis=0)
            NablaY = numpy.diff(paddedField,axis=1)
            xAbs   = (NablaX[:,:-1]/dx[:,pylab.NewAxis])**2
            yAbs   = (NablaY[:-1,:]/dy[pylab.NewAxis,:])**2

        gradient = numpy.sqrt(xAbs + yAbs)
#        print image.data
#        print NablaX
#        print NablaY
        #print gradient

        newUnit = unit(image.unit) / unit(image.dimensions[0].unit)
        result = DataContainer.FieldContainer(gradient,
                                              unit = newUnit,
                                              dimensions=copy.deepcopy(image.dimensions),
                                              longname=u"Slope of %s" % image.longname,
                                              shortname=u"|\nabla %s|" % image.shortname,
                                              rescale = True)
        result.seal()
        return result

