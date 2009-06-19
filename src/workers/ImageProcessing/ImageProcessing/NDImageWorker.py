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
from scipy import (ndimage, interpolate)

def pile(func, imagedata):
    assert imagedata.ndim in [2, 3]
    if imagedata.ndim == 2:
        pile = [imagedata]
    else:
        pile = imagedata
    pile = [func(data) for data in pile]
    if imagedata.ndim == 2:
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
                "maximum_filter":("size", )}
    _ndparams = {"iterations":1,
                 "size":5}
    _params = [("pile", "Treat 3d images as pile of 2d images", True, None),
               ("ndfilter", "Filter", _filters.keys(), None)]
    _params += [(pn, pn, dflt, None) for pn, dflt in _ndparams.iteritems()]

    def watershed_ift(self, data):
        return ndimage.watershed_ift(data, data)

    def applyfilter(self, data):
        fltparams = ''
        for par in self._filters[self.paramNdfilter.value]:
            if par != None:
                fltparams += ', %s=%s' % (par, self.getParam(par).value)
        if None in self._filters[self.paramNdfilter.value]:
            call = "self"
        else:
            call = "ndimage"
        todostr = "%s.%s(data%s)" % (call, self.paramNdfilter.value,
                                     fltparams)
        return eval(todostr)

    @Worker.plug(Connectors.TYPE_IMAGE)
    def ndimage(self, image, subscriber=0):
        if self.paramPile.value:
            newdata = pile(self.applyfilter, image.data)
        else:
            newdata = self.applyfilter(image.data)
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
