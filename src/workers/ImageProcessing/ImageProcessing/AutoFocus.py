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
from pyphant.quantities.PhysicalQuantities import (isPhysicalQuantity,
                                                   PhysicalQuantity)

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

    def __eq__(self, other):
        return self.slices == other.slices

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

    def getCenter(self):
        return tuple([(sli.start + sli.stop) / 2.0 for sli in self.slices])


class FocusSlice(Cube):
    def __init__(self, slices, focus, mask):
        Cube.__init__(self, slices)
        self.focus = focus
        self.mask = mask

    def __str__(self):
        retstr = "FocusSlice(slices=%s, focus=%s, mask=%s)"
        return retstr % (self.slices, self.focus, self.mask)

    def __repr__(self):
        retstr = "FocusSlice(%s, %s, %s)"
        return retstr % (self.slices.__repr__(),
                         self.focus.__repr__(),
                         self.mask.__repr__())

    def __eq__(self, other):
        eqflag = self.slices == other.slices
        eqflag &= self.focus == other.focus
        eqflag &= (self.mask == other.mask).all()
        return eqflag


class ZTube(object):
    def __init__(self, fslice, zvalue, ztol, boundRatio, featureRatio):
        self.yxCube = Cube(fslice.slices)
        self.maxFocus = fslice.focus
        self.focusedFSlice = fslice
        self.boundRatio = boundRatio
        self.featureRatio = featureRatio
        self.zCube = Cube([slice(zvalue - ztol, zvalue + ztol)])
        self.ztol = ztol
        self.focusedZ = zvalue

    def match(self, fslice, zvalue):
        vol = (self.yxCube & fslice).getVolume()
        if not isPhysicalQuantity(vol):
            vol = float(vol)
        yxratio = vol / fslice.getVolume()
        fszCube = Cube([slice(zvalue - self.ztol, zvalue + self.ztol)])
        zmatch = self.zCube & fszCube
        print zmatch.getVolume(), yxratio
        if yxratio >= self.boundRatio and zmatch.getVolume() != 0:
            orCube = self.yxCube | fslice
            self.yxCube = orCube
            self.zCube = self.zCube | fszCube
            if fslice.focus > self.maxFocus:
                self.maxFocus = fslice.focus
                self.focusedFSlice = fslice
                self.focusedZ = zvalue
            return True
        return False

    def getFocusedInclusion(self):
        """
        This method returns a tuple
        (z, y, x, diameter, focus, zError, yError, xError, diameterError)
        corresponding to the most focused feature in the ZTube
        """
        #This is just a preliminary example of how to calculate the values...
        coordY, coordX = self.focusedFSlice.getCenter()
        coordZ = self.focusedZ
        edgeL0 = self.focusedFSlice.getEdgeLength(0)
        edgeL1 = self.focusedFSlice.getEdgeLength(1)
        cEZ, cEY, cEX = self.ztol, edgeL0 / 4.0, edgeL1 / 4.0
        diameter = (edgeL0 * edgeL0 + edgeL1 * edgeL1) ** .5
        diameterError = .1 * diameter
        return (coordZ, coordY, coordX, diameter, self.focusedFSlice.focus,
                cEZ, cEY, cEX, diameterError)


def autofocus(focusfc, boundRatio, featureRatio):
    ztubes = []
    ztol = focusfc.attributes[u'ztol']
    for zNumValue, focusData in zip(focusfc.dimensions[0].data, focusfc.data):
        zvalue = zNumValue * focusfc.dimensions[0].unit
        for fslice in focusData:
            matched = False
            for ztube in ztubes:
                matched = ztube.match(fslice, zvalue)
                if matched:
                    break
            if not matched:
                ztubes.append(ZTube(fslice, zvalue, ztol,
                                    boundRatio, featureRatio))
    if ztubes == []:
        return []
    fInclusions = [ztube.getFocusedInclusion() for ztube in ztubes]
    longnames = ["z-value", "y-value", "x-value", "diameter", "focus"]
    shortnames = ["z", "y", "x", "d", "f"]
    fIColumns = zip(*fInclusions)
    pqdata = [fIColumns[index] for index in xrange(5)]
    pqerrors = [fIColumns[index] for index in xrange(5, 9)]
    units = [PhysicalQuantity(1, fInclusions[0][index].unit) \
                 for index in xrange(5)]
    data = [numpy.array([spqd.inUnitsOf(pqunit.unit).value for spqd in pqd]) \
                for pqd, pqunit in zip(pqdata, units)]
    errors = [numpy.array([serr.inUnitsOf(pqunit.unit).value for serr in err]) \
                  for err, pqunit in zip(pqerrors, units[:4])]
    errors.append(None)
    return [DataContainer.FieldContainer(dat, unit, err,
                                         longname=ln, shortname=sn) \
                for dat, unit, err, ln, sn in zip(data, units, errors,
                                                  longnames, shortnames)]


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

    @Worker.plug(Connectors.TYPE_ARRAY)
    def AutoFocusWorker(self, focusfc, subscriber=0):
        columns = autofocus(focusfc,
                            self.paramBoundRatio.value,
                            self.paramFeatureRatio.value)
        longname = "AutoFocus"
        result = DataContainer.SampleContainer(columns=columns,
                                              longname=longname)
        result.seal()
        return result
