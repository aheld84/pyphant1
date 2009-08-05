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
from pyphant.quantities.PhysicalQuantities import isPhysicalQuantity

class Cube(object):
    def __init__(self, slices):
        self.slices = slices

    def _binary(self, other, bifunc1, bifunc2):
        bislices = []
        for sli1, sli2 in zip(self.slices, other.slices):
            bislice = slice(bifunc1(sli1.start, sli2.start),
                            bifunc2(sli1.stop, sli2.stop))
            if bislice.stop < bislice.start:
                bislice = slice(0, 0)
            bislices.append(bislice)
        return Cube(bislices)

    def __and__(self, other):
        return self._binary(other, max, min)

    def __or__(self, other):
        return self._binary(other, min, max)

    def __eq__(self, other, rtol=1e-5, atol=1e-8):
        if len(self.slices) != len(other.slices):
            return False
        for index in xrange(len(self.slices)):
            if self.slices[index] != other.slices[index]:
                return False
        return True

    def __sub__(self, other):
        subslices = []
        for sli1, sli2 in zip(self.slices, other.slices):
            sub = sli2.start
            subslices.append(slice(sli1.start - sub, sli1.stop - sub))
        return Cube(subslices)

    def getSubCube(self, dimlist):
        subslices = []
        for dim in xrange(len(self.slices)):
            if dim in dimlist:
                subslices.append(self.slices[dim])
        return Cube(subslices)

    def getVolume(self):
        vol = 1
        for sli in self.slices:
            vol *= (sli.stop - sli.start)
        return vol

    def getEdgeLength(self, edgeIndex):
        return self.slices[edgeIndex].stop - self.slices[edgeIndex].start


class FocusSlice(Cube):
    def __init__(self, slices, focus, mask, label):
        Cube.__init__(self, slices)
        self.focus = focus
        self.mask = mask
        self.label = label
        self.size = mask.sum()


class ZTube(list, FocusSlice):
    def __init__(self, fslice, boundRatio, featureRatio):
        FocusSlice.__init__(self, fslice.slices, fslice.focus,
                            fslice.mask, 1)
        self.append(fslice)
        self.boundRatio = boundRatio
        self.featureRatio = featureRatio
        self.focusedIndex = 0

    def match(self, fslice):
        subCube1 = self.getSubCube([1, 2])
        subCube2 = fslice.getSubCube([1, 2])
        vol = (subCube1 & subCube2).getVolume()
        if not isPhysicalQuantity(vol):
            vol = float(vol)
        yxratio = vol / subCube2.getVolume()
        zmatch = self.getSubCube([0]) & fslice.getSubCube([0])
        if yxratio >= self.boundRatio and zmatch.getVolume() != 0:
            #TODO: feature matching
            orCube = self | fslice
            maskSlices1 = (self - orCube).getSubCube([1, 2]).slices
            maskSlices2 = (fslice - orCube).getSubCube([1, 2]).slices
            newmask = numpy.zeros((orCube.getEdgeLength(1),
                                   orCube.getEdgeLength(2)),
                                  dtype=bool)
            newmask[maskSlices1] = self.mask
            newmask[maskSlices2] |= fslice.mask
            self.mask = newmask
            self.slices = orCube.slices
            self.append(fslice)
            if fslice.focus > self.focus:
                self.focus = fslice.focus
                self.focusIndex = len(self) - 1
            return True
        return False

def autofocus(focusfc, boundRatio, featureRatio):
    ztubes = []
    for fslice in focusfc.data:
        matched = False
        for ztube in ztubes:
            matched = ztube.match(fslice)
            if matched:
                break
        if not matched:
            ztubes.append(ZTube(fslice, boundRatio, featureRatio))
    for ztube in ztubes:
        pass


class AutoFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "AutoFocus"
    _params = [("boundRatio", "Minimal overlap ratio (bounding box)",
                0.5, False),
               ("featureRatio", "Minimal overlap ratio (feature area)",
                0.75, False)]
    _sockets = [("focusfc", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def AutoFocusWorker(self, focusfc, subscriber=0):
        newdata = autofocus(focusfc,
                            self.paramBoundRatio.value,
                            self.paramFeatureRatio.value)
        longname = "AutoFocus"
        result = DataContainer.FieldContainer(
            data=newdata,
            longname=longname)
        result.seal()
        return result
