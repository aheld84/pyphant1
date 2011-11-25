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

from pyphant.core import (Worker, Connectors, DataContainer)
import copy
import heapq
import scipy
import scipy.ndimage
#import pylab
#import threading


class Watershed(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Watershed"
    _sockets = [("image", Connectors.TYPE_IMAGE),
                ("markers", Connectors.TYPE_IMAGE)]
    #_params = [("maxmin", "max/min", ["max", "min"], None),
    #          ("domn", "dominates neighbours by", 0, None)]

    def watershed(self, a):
        m = self._markers
        #d = scipy.ndimage.distance_transform_edt(a)
        d = a.copy()
        q = []
        w = m.copy()
        for y, x in scipy.argwhere(m != 0):
            heapq.heappush(q, (-d[y - 1, x - 1], (y - 1, x - 1)))
            heapq.heappush(q, (-d[y - 1, x], (y - 1, x)))
            heapq.heappush(q, (-d[y - 1, x + 1], (y - 1, x + 1)))
            heapq.heappush(q, (-d[y, x - 1], (y, x - 1)))
            heapq.heappush(q, (-d[y, x + 1], (y, x + 1)))
            heapq.heappush(q, (-d[y + 1, x - 1], (y + 1, x - 1)))
            heapq.heappush(q, (-d[y + 1, x], (y + 1 , x)))
            heapq.heappush(q, (-d[y + 1, x + 1], (y + 1, x + 1)))
        while q:
            y, x = heapq.heappop(q)[1]
            l = scipy.unique(w[y - 1: y + 2, x - 1: x + 2])
            l = l[l != 0]
            if len(l) == 1:
                w[y, x] = l[0]
            for ny, nx in scipy.argwhere(w[y - 1: y + 2, x - 1: x + 2] == 0):
                if (ny == 1) and (nx == 1):
                    continue
                ny += y - 1
                nx += x - 1
                try:
                    p = (-d[ny, nx], (ny, nx))
                    d[ny, nx] = 0
                    if p[0] != 0 and not p in q:
                        heapq.heappush(q, p)
                except IndexError, e:
                    print e
        return w

    @Worker.plug(Connectors.TYPE_IMAGE)
    def wsworker(self, image, markers, subscriber=0):
        self._markers = markers.data
        newdata = self.watershed(image.data)
        longname = "Watershed"
        result = DataContainer.FieldContainer(newdata,
                                              copy.deepcopy(image.unit),
                                              copy.deepcopy(image.error),
                                              copy.deepcopy(image.mask),
                                              copy.deepcopy(image.dimensions),
                                              longname,
                                              image.shortname,
                                              copy.deepcopy(image.attributes),
                                              False)
        result.seal()
        #print newdata.shape
        return result
