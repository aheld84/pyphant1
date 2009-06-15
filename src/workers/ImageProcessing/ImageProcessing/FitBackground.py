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
               ("swidth", "sample width", 100, None),
               ("sheight", "sample height", 100, None),
               ("threshold", "Background threshold", 60, None)]

    def fit(self, data, background, poldegree, swidth, sheight, threshold):
        dims = data.shape
        xList = []
        yList = []
        zList = []
        for y in xrange(0, dims[0] - 1, sheight):
            for x in xrange(0, dims[1] - 1, swidth):
                view = data[y:y + sheight, x:x + swidth]
                if background == self._bgbright:
                    flatIndex = numpy.argmax(view)
                elif background == self._bgdark:
                    flatIndex = numpy.argmin(view)
                else:
                    raise ValueError("Parameter 'background' not set.")
                yIdx, xIdx = numpy.unravel_index(flatIndex, view.shape)
                zValue = view[yIdx, xIdx]
                if (background == self._bgdark and zValue <= threshold) or\
                        (background == self._bgbright and zValue >= threshold):
                    xList.append(x + xIdx)
                    yList.append(y + yIdx)
                    zList.append(zValue)
        if len(xList) < (poldegree + 1) * (poldegree + 1):
            raise ValueError("Not enough reference points.")
        tck = interpolate.bisplrep(yList, xList, zList,
                                   kx=poldegree, ky=poldegree,
                                   xb=0, yb=0,
                                   xe=int(dims[0]), ye=int(dims[1]))
        if background == self._bgbright:
            clipmin, clipmax = threshold, data.max()
        elif background == self._bgdark:
            clipmin, clipmax = data.min(), threshold
        return interpolate.bisplev(range(dims[0]), range(dims[1]),
                                   tck).clip(clipmin, clipmax)


    @Worker.plug(Connectors.TYPE_IMAGE)
    def fit_background(self, image, subscriber=0):
        background = self.paramBackground.value
        poldegree = self.paramPoldegree.value
        swidth = self.paramSwidth.value
        sheight = self.paramSheight.value
        threshold = self.paramThreshold.value
        newdata = self.fit(image.data, background,
                           poldegree, swidth, sheight, threshold)
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
