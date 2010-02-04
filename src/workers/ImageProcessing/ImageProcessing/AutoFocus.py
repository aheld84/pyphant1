# -*- coding: utf-8 -*-

# Copyright (c) 2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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
from pyphant.quantities import (isQuantity,
                                                   Quantity)
from pyphant.core.DataContainer import FieldContainer


class Cube(object):
    def __init__(self, slices):
        self.slices = slices

    def _binary(self, other, bifunc1, bifunc2):
        bislices = []
        for sli1, sli2 in zip(self.slices, other.slices):
            bislice = slice(bifunc1(sli1.start, sli2.start),
                            bifunc2(sli1.stop, sli2.stop))
            if bislice.stop < bislice.start:
                # Weird notation necessary for PhysicalQuantities!
                bislice = slice(0 * bislice.start, 0 * bislice.stop)
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
    def __init__(self, slices, focus, mask_parent, mask_slices):
        Cube.__init__(self, slices)
        self.focus = focus
        self.mask_parent = mask_parent
        self.mask_slices = mask_slices
        self._mask = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retstr = "FocusSlice(%s, %s, %s, %s)"
        return retstr % (self.slices.__repr__(),
                         self.focus.__repr__(),
                         self.mask_parent.__repr__(),
                         self.mask_slices.__repr__())

    def __eq__(self, other):
        if isinstance(other, FocusSlice):
            eqflag = self.slices == other.slices
            eqflag &= self.focus == other.focus
            eqflag &= (self.mask == other.mask).all()
            return eqflag
        else:
            return False

    def getMask(self):
        if self._mask == None:
            from pyphant.core.KnowledgeManager import KnowledgeManager
            km = KnowledgeManager.getInstance()
            self._mask = km.getDataContainer(
                self.mask_parent).data[self.mask_slices]
        return self._mask
    mask = property(getMask)


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
        if not isQuantity(vol):
            vol = float(vol)
        yxratio = 2.0 * vol / (fslice.getVolume() + self.yxCube.getVolume())
        fszCube = Cube([slice(zvalue - self.ztol, zvalue + self.ztol)])
        zvol = (self.zCube & fszCube).getVolume()
        # weird notation necessary for PhysicalQuantities
        if yxratio >= self.boundRatio and zvol != 0 * zvol:
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


def autofocus(focusSC, boundRatio, featureRatio):
    from pyphant.core.KnowledgeManager import KnowledgeManager
    km = KnowledgeManager.getInstance()
    ztubes = []
    ztol = focusSC.attributes[u'ztol']
    zunit = focusSC['z-value'].unit
    for zNumValue, emd5 in zip(focusSC['z-value'].data, focusSC['emd5'].data):
        zvalue = zNumValue * zunit
        focusFC = km.getDataContainer(unicode(emd5).encode('utf-8'))
        for fslice in focusFC.data:
            if fslice != 0:
                if not isinstance(fslice, FocusSlice):
                    print fslice
                    raise ValueError("Should be FocusSlice object!")
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
    units = [Quantity(1, fInclusions[0][index].unit) \
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
    _params = [("boundRatio", "Minimal overlap ratio in percent (bounding box)",
                50, None),
               ("featureRatio",
                "Not implemented", 75, None)]
    _sockets = [("focusSC", Connectors.TYPE_ARRAY)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def AutoFocusWorker(self, focusSC, subscriber=0):
        columns = autofocus(focusSC,
                            self.paramBoundRatio.value / 100.0,
                            self.paramFeatureRatio.value / 100.0)
        longname = "AutoFocus"
        result = DataContainer.SampleContainer(columns=columns,
                                              longname=longname)
        result.seal()
        return result
