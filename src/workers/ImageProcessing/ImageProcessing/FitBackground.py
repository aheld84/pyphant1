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
Deprecated
"""

__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, DataContainer)
import numpy
import copy
from scipy import (ndimage, interpolate)

class FitBackground(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Fit Background"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("poldegree", "Polynomial degree (1 to 5)", 3, None),
               ("swidth", "sample width", 150, None),
               ("sheight", "sample height", 150, None),
               ("threshold", "Background threshold", 255, None),
               ("mediansize", "Median kernel size", 3, None),
               ("medianruns", "Median runs", 3, None),
               ("darksize", "Erosion kernel size", 3, None),
               ("darkruns", "Erosion runs", 4, None),
               ("brightsize", "Inverted erosion size", 6, None),
               ("brightruns", "Inverted erosion runs", 10, None),
               ("dopreview", "Preview fit input", False, None)]

    def fit(self, data, poldegree, swidth, sheight, threshold):
        if int(threshold) == -1:
            threshold = (int(data.mean()) * 10) / 7
        dims = data.shape
        xList = []
        yList = []
        zList = []
        for y in xrange(0, dims[0] - 1, sheight):
            for x in xrange(0, dims[1] - 1, swidth):
                view = data[y:y + sheight, x:x + swidth]
                flatIndex = numpy.argmax(view)
                yIdx, xIdx = numpy.unravel_index(flatIndex, view.shape)
                zValue = view[yIdx, xIdx]
                if zValue <= threshold:
                    xList.append(x + xIdx)
                    yList.append(y + yIdx)
                    zList.append(zValue)
        if len(xList) < (poldegree + 1) * (poldegree + 1):
            raise ValueError("Not enough reference points.")
        tck = interpolate.bisplrep(yList, xList, zList,
                                   kx=poldegree, ky=poldegree,
                                   xb=0, yb=0,
                                   xe=int(dims[0]), ye=int(dims[1]))
        clipmin, clipmax = data.min(), threshold
        return interpolate.bisplev(range(dims[0]), range(dims[1]),
                                   tck).clip(clipmin, clipmax)


    @Worker.plug(Connectors.TYPE_IMAGE)
    def fit_background(self, image, subscriber=0):
        poldegree = int(self.paramPoldegree.value)
        swidth = int(self.paramSwidth.value)
        sheight = int(self.paramSheight.value)
        threshold = int(self.paramThreshold.value)
        mediansize = int(self.paramMediansize.value)
        medianruns = int(self.paramMedianruns.value)
        darksize = int(self.paramDarksize.value)
        darkruns = int(self.paramDarkruns.value)
        brightsize = int(self.paramBrightsize.value)
        brightruns = int(self.paramBrightruns.value)
        dopreview = self.paramDopreview.value
        data = image.data
        #Median:
        for run in xrange(medianruns):
            data = ndimage.median_filter(data, size=mediansize)
        #Suspend dark spots:
        for run in xrange(darkruns):
            data = 255 - ndimage.grey_erosion(255 - data, size=darksize)
        #Suspend features:
        for run in xrange(brightruns):
            data = ndimage.grey_erosion(data, size=brightsize)
        #Fit background:
        if not dopreview:
            data = self.fit(data, poldegree, swidth, sheight, threshold)
        longname = "FitBackground"
        result = DataContainer.FieldContainer(
            data,
            copy.deepcopy(image.unit),
            copy.deepcopy(image.error),
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
