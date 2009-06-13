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

class FitBackground(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "FitBackground"
    _bgdark = "dark"
    _bgbright = "bright"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("background",
                "Background(dark/bright)",
                [_bgdark, _bgbright],
                None),
               ("poldegree", "Polynomial degree (1 to 5)", 3, None),
               ("samples", "#samples per dimension", 30, None)]

    def fit(self, data, background, poldegree, samples):
        dims = data.shape
        windowWidth, windowHeight = [ d/samples for d in dims ]
        xList = []
        yList = []
        zList = []
        for x in xrange(samples):
            for y in xrange(samples):
                xOffset = x * windowWidth
                yOffset = y * windowHeight
                view = data[xOffset:xOffset + windowWidth,
                            yOffset:yOffset + windowHeight]
                if background == self._bgbright:
                    flatIndex = numpy.argmax(view)
                else:
                    flatIndex = numpy.argmin(view)
                xIdx, yIdx = numpy.unravel_index(flatIndex, view.shape)
                xList.append(xOffset + xIdx)
                yList.append(yOffset + yIdx)
                zList.append(view[xIdx, yIdx])
        #print zip(xList, yList, zList)
        tck = interpolate.bisplrep(xList, yList, zList,
                                   kx=poldegree, ky=poldegree)
        return interpolate.bisplev(range(dims[0]), range(dims[1]), tck)


    @Worker.plug(Connectors.TYPE_IMAGE)
    def fit_background(self, image, subscriber=0):
        background = self.paramBackground.value
        poldegree = self.paramPoldegree.value
        samples = self.paramSamples.value
        newdata = self.fit(image.data, background, poldegree, samples)
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
