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
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer
import ImageProcessing
import numpy, copy
from scipy import (ndimage, interpolate, vectorize)

def pile(func, imagedata, runs=1, dopile=True):
    assert imagedata.ndim in [2, 3]
    assert runs >= 0
    if runs == 0:
        return imagedata
    if imagedata.ndim == 2 or not dopile:
        pile = [imagedata]
    else:
        pile = imagedata
    for run in xrange(runs):
        pile = [func(data) for data in pile]
    if imagedata.ndim == 2 or not dopile:
        newdata = pile[0]
    else:
        newdata = numpy.array(pile)
    return newdata


class NDImage(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "ndimage"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _filters = {"binary_closing":("iterations", ),
                "binary_opening":("iterations", ),
                "binary_fill_holes":(),
                #"watershed_ift":(None, ),
                "maximum_filter":("size", "mode", "cval"),
                "median_filter":("size", "mode", "cval"),
                "grey_closing":("size", "mode", "cval"),
                "grey_dilation":(None, "size", "mode", "cval"),
                "grey_erosion":("size", "mode", "cval"),
                "grey_opening":("size", "mode", "cval"),
                "cut_histogram":(None, "tolerance"),
                "gradient":(None, ),
                "label":(None, "connectivity")}
    _ndparams = {"iterations":1,
                 "size":5,
                 "mode":["reflect",
                         "nearest",
                         "wrap",
                         "constant"],
                 "cval":0,
                 "tolerance":1000,
                 "connectivity":2}
    _params = [("pile", "Treat 3d images as pile of 2d images", True, None),
               ("ndfilter", "Filter", _filters.keys(), None)]
    _params += [(pn, pn, dflt, None) for pn, dflt in _ndparams.iteritems()]

    #def watershed_ift(self, data):
        #return ndimage.watershed_ift(data, data)

    def gradient(self, data):
        res = numpy.sqrt(sum(
                numpy.square(numpy.array(numpy.gradient(data)))
                ))
        return (res * 255.0).astype(int) / 361

    def grey_dilation(self, data, size, mode):
        return 255 - ndimage.grey_erosion(255 - data, size=size, mode=mode)

    def label(self, data, connectivity):
        structure = ndimage.morphology.generate_binary_structure(data.ndim,
                                                               connectivity)
        return ndimage.label(data, structure=structure)[0]

    def cut_histogram(self, data, tolerance):
        h = ndimage.histogram(data, 0, 256, 256)
        cs = numpy.cumsum(h)
        cut = cs[255] / tolerance
        for i in xrange(len(cs)):
            if cs[i] > cut:
                newmin = i
                break
        m = data.mean()
        return numpy.where(data < newmin, m, data)

    def applyfilter(self, data):
        if None in self._filters[self.paramNdfilter.value]:
            call = getattr(self, self.paramNdfilter.value)
        else:
            call = getattr(ndimage, self.paramNdfilter.value)
        args = {}
        for par in self._filters[self.paramNdfilter.value]:
            if par != None:
                args[par] = self.getParam(par).value
        print args
        return call(data, **args)

    @Worker.plug(Connectors.TYPE_IMAGE)
    def ndimage(self, image, subscriber=0):
        if "iterations" in self._filters[self.paramNdfilter.value]:
            runs = 1
        else:
            runs = self.paramIterations.value
        newdata = pile(self.applyfilter, image.data, runs, self.paramPile.value)
        result = DataContainer.FieldContainer(
            newdata,
            copy.deepcopy(image.unit),
            copy.deepcopy(image.error),
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            image.longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
