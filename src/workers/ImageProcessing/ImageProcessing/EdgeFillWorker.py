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
The Edge Fill Worker is a class of Pyphant's Image Processing
Toolbox. It is used to backfill outlined features again.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors)
import copy
from ImageProcessing import (BACKGROUND_COLOR, FEATURE_COLOR)


class EdgeFillWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    """
    http://www.nabble.com/Here's-a-better-flood-fill-technique-t318692.html
    """
    name = "Edge Fill"
    _sockets = [("image", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def fillImage(self, image, subscriber=0):
        result = copy.deepcopy(image)
        im = result.data
        self.fillFromEdge(im, BACKGROUND_COLOR, FEATURE_COLOR)
        result.seal()
        return result

    def fillFromEdge(self, image, seedColor, newColor):
        def filterSeeds(im, potSeeds):
            pos = potSeeds.pop(0)
            seeds = [pos]
            color = im[pos]
            while potSeeds:
                pos = potSeeds.pop(0)
                if im[pos] != color:
                    seeds.append(pos)
                    color = im[pos]
            return seeds
        maxX = image.shape[0]
        maxY = image.shape[1]
        seeds = filterSeeds(image,
                            [(x, 0) for x in range(0, maxX)] \
                            + [(maxX - 1, y) for y in range(1, maxY - 1)] \
                            + [(x, maxY - 1) for x in range(maxX - 1, -1, -1)] \
                            + [(0, y) for y in range(maxY - 2, 0, -1)])
        seeds = filter(lambda pos: image[pos] == seedColor, seeds)
        map(lambda pos: self.fillRegion(image, pos, newColor), seeds)

    def fillRegion(self, image, seed, newcolor):
        oldcolor = image[seed]
        if oldcolor == newcolor:
            return
        edge = [seed]
        maxX = image.shape[0]
        maxY = image.shape[1]
        while edge:
            newedge = []
            for (x, y) in edge:
                for (s, t) in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if s >= 0 and s < maxX and t >= 0 and t < maxY \
                           and image[s, t] == oldcolor:
                        image[s, t] = newcolor
                        newedge.append((s, t))
                edge = newedge
