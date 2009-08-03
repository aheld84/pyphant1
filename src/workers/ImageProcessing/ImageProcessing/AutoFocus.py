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
from scipy import ndimage as ndi


class Cube(object):
    def __init__(self, slices):
        self.slices = slices

    def __and__(self, other):
        andslices = []
        for index in xrange(len(self.slices)):
            sli1 = self.slices[index]
            sli2 = other.slices[index]
            andslice = slice(max(sli1.start, sli2.start),
                             min(sli1.stop, sli2.stop)))
            if andslice.stop < andslice.start:
                andslice = slice(0, 0)
            andslices.append(andslice)
        return Cube(andslices)

    def __or__(self, other):
        # TODO
        pass

    def getVolume(self):
        vol = 1
        for sli in self.slices:
            vol *= (sli.stop - sli.start)
        return vol


class FocusSlice(Cube):
    def __init__(self, slices, focus, mask, label):
        Cube.__init__(self, slices)
        self.focus = focus
        self.mask = mask
        self.label = label
        self.size = mask.sum()


class ZTube(list):
    def __init__(self, fslice, matchRatio):
        self.matchCube = Cube(fslice.slices)
        self.append(fslice)
        self.matchRatio = matchRatio

    def match(self, fslice):
        ratio = (self.matchCube & fslice).getVolume() / fslice.getVolume()
        if ratio >= self.matchRatio:
            self.matchCube = self.matchCube | fslice
            self.append(fslice)
            return True
        return False

def autofocus(focusfc, matchRatio):
    ztubes = []
    for fslice in focusfc.data:
        matched = False
        for ztube in ztubes:
            matched = ztube.match(fslice)
            if matched:
                break
        if not matched:
            ztubes.append(ZTube(fslice, matchRatio))
    for ztube in ztubes:
        pass


class AutoFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "AutoFocus"
    _params = [("matchRatio", "Minimal matching ratio", 0.75, False)]
    _sockets = [("focusfc", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def AutoFocusWorker(self, focusfc, subscriber=0):
        newdata = autofocus(focusfc, self.paramMatchRatio.value)
        longname = "AutoFocus"
        result = DataContainer.FieldContainer(
            data=newdata,
            longname=longname)
        result.seal()
        return result
