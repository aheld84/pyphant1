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

from pyphant.core import (Worker, Connectors)
import copy
from scipy import ndimage
from numpy import (alltrue, zeros, int32)
import pkg_resources


class FindLocalExtrema(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Local Extrema"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("maxmin", "max/min", ["max", "min"], None),
               ("excolor", "marker color (-1 for labeling)", 255, None),
               ("tolerance", "tolerance in %", 20, None)]

    def compare(self, pvalue, nhood, viewextr):
        if self.paramMaxmin.value == "max":
            c = pvalue >= (viewextr * (100 - self.paramTolerance.value)) / 100
        else:
            c = pvalue <= (viewextr * (100 + self.paramTolerance.value)) / 100
        return c

    def getPoints(self, data, sl):
        if sl[0].stop - sl[0].start < 3 or sl[1].stop - sl[1].start < 3:
            return []
        points = []
        if self.paramMaxmin.value == "max":
            viewextr = data[sl].max()
        else:
            viewextr = data[sl].min()
        for y in xrange(sl[0].start, sl[0].stop):
            ydiff = 1
            if y == 0:
                ydiff = 0
            for x in xrange(sl[1].start, sl[1].stop):
                xdiff = 1
                if x == 0:
                    xdiff = 0
                nhood = data[y - ydiff:y + 2,
                             x - xdiff:x + 2]
                pvalue = data[y, x]
                if not alltrue(pvalue == nhood):
                    if self.compare(pvalue, nhood, viewextr):
                        if self.paramExcolor.value == -1:
                            color = self.nextlabel
                        else:
                            color = self.paramExcolor.value
                        points.append(((y, x), color))
                        self.nextlabel += 1
        return points

    def findExtrema(self, data):
        labeled = ndimage.label(data, output=int32)[0]
        self.nextlabel = 1
        slices = ndimage.find_objects(labeled)
        res = zeros(data.shape, int)
        for sl in slices:
            points = self.getPoints(data, sl)
            for p, c in points:
                res[p] = c
        return res

    @Worker.plug(Connectors.TYPE_IMAGE)
    def find(self, image, subscriber=0):
        newdata = self.findExtrema(image.data)
        longname = "FindLocalExtrema"
        from pyphant.core.DataContainer import FieldContainer
        result = FieldContainer(
            newdata,
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
