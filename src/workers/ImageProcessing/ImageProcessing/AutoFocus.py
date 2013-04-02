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
This module provides the refactored AutoFocus Worker and its little helpers
"""


from pyphant.core import (Worker, Connectors)
import numpy
from scipy import ndimage
from pyphant.quantities import Quantity
from pyphant.core.DataContainer import SampleContainer

def sobel(data):
    return numpy.sqrt(ndimage.sobel(data, 0) ** 2 + \
                      ndimage.sobel(data, 1) ** 2)


class ZSUnits(object):
    FQUANT = Quantity('1.0 mum**-3')
    FUNIT = FQUANT.unit
    AQUANT = Quantity('1.0 mum**2')
    AUNIT = AQUANT.unit
    GQUANT = Quantity('1.0 mum**-1')
    GUNIT = GQUANT.unit
    NODNS = "Non-uniform dimensions not supported!"
    DXDY = NODNS + "\ndy = %s\ndx = %s"
    DUW = "Dimension unit has to be compatible to 'm'!"

    def __init__(self, image):
        assert image.unit == 1
        self.dims = image.dimensions
        assert self.dims[1].unit == self.dims[2].unit, self.NODNS
        try:
            dy = image.attributes['yFactor']
        except KeyError:
            dy = numpy.average(numpy.diff(self.dims[1].data)) \
                 * self.dims[1].unit
        try:
            dx = image.attributes['xFactor']
        except KeyError:
            dx = numpy.average(numpy.diff(self.dims[2].data)) \
                 * self.dims[2].unit
        tolPercent = 2 # reasonable?
        assert abs(dy - dx) / dy <= tolPercent / 100., \
               self.DXDY % (dy.__repr__(), dx.__repr__())
        self.delta = dy
        gunit = self.dims[1].unit ** -1
        aunit = dy * dx
        funit = gunit / aunit
        self.gmul = gunit / self.GQUANT
        self.amul = aunit / self.AQUANT
        self.fmul = funit / self.FQUANT
        assert isinstance(self.gmul, float), self.DUW
        assert isinstance(self.amul, float), self.DUW
        assert isinstance(self.fmul, float), self.DUW


class Inclusion(object):
    TWO_TIMES_SQRT_ONE_OVER_PI = 1.1283791670

    def __init__(self, zind, label, slices, dataDetail, footprint, zsp, zsu):
        if footprint.sum() <= zsp.ath:
            self.valid = False
            return
        self.label = label
        self.zind = zind
        self.preds = []
        self.succs = []
        sobel = numpy.sqrt(ndimage.sobel(dataDetail, 0) ** 2 + \
                           ndimage.sobel(dataDetail, 1) ** 2)
        def focusFootprint(fpd):
            return (numpy.where(fpd[1], sobel, 0.0).sum() / fpd[1].sum(),
                    fpd[0])
        fpDict = {}
        fpDict[0] = footprint
        fpDict[1] = ndimage.binary_dilation(footprint)
        fpDict[2] = ndimage.binary_dilation(fpDict[1])
        fpDict[-1] = ndimage.binary_erosion(footprint)
        fpDict[-2] = ndimage.binary_erosion(fpDict[-1])
        fpDilList = [(fpDict[i], fpDict[i + 1]) for i in xrange(-2, 2)]
        ffpList = [focusFootprint(fpDil) for fpDil in fpDilList]
        maxffp = max(ffpList, key=lambda x: x[0])
        area = maxffp[1].sum()
        if area <= zsp.ath:
            self.valid = False
            return
        self.valid = True
        self.focus = maxffp[0] * zsu.fmul
        self.footprint = maxffp[1]
        self.area = area * zsu.amul
        islices = ndimage.find_objects(self.footprint)[0]
        self.slices = [slice(sli.start + isli.start, sli.start + isli.stop) \
                       for sli, isli in zip(slices, islices)]
        self.fpSlices = slices
        self.centerOfMass = ndimage.center_of_mass(self.footprint)
        self.centerOfMass = (self.centerOfMass[0] + slices[0].start,
                             self.centerOfMass[1] + slices[1].start)

    @property
    def diameter(self):
        return self.TWO_TIMES_SQRT_ONE_OVER_PI \
               * (self.area * ZSUnits.AQUANT).sqrt()

    def getInfo(self, zsu):
        coordZ = zsu.dims[0].data[self.zind] * zsu.dims[0].unit
        coordY = self.centerOfMass[0] * zsu.delta \
                 + zsu.dims[1].data[0] * zsu.dims[1].unit
        coordX = self.centerOfMass[1] * zsu.delta \
                 + zsu.dims[2].data[0] * zsu.dims[2].unit
        return (coordZ, coordY, coordX, self.diameter,
                self.focus * ZSUnits.FQUANT, self.label, self.zind,
                self.slices[0].start, self.slices[0].stop,
                self.slices[1].start, self.slices[1].stop)

    def append(self, inclusion):
        self.succs.append(inclusion)
        inclusion.preds.append(self)

    def invalidateConnected(self):
        self.invalidatePreds()
        self.invalidateSuccs()

    def invalidatePreds(self):
        self.valid = False
        for i in self.preds:
            i.invalidatePreds()

    def invalidateSuccs(self):
        self.valid = False
        for i in self.succs:
            i.invalidateSuccs()

    @property
    def index(self):
        return (self.zind, self.label)


class ZSParams(object):
    def __init__(self, worker):
        self.ath = int(worker.paramAreaThreshold.value)
        split = worker.paramMedianSize.value.split(',')
        self.significance = float(worker.paramSignificance.value)
        self.medianZoom = int(worker.paramMedianZoom.value)
        self.medianSize = (int(split[0].replace('(', '')) / self.medianZoom,
                           int(split[1].replace(')', '')) / self.medianZoom)
        self.threshold = None

    def estimateThreshold(self, data, subscriber):
        interest = numpy.zeros(data.shape, dtype=float)
        maxi = float(data.shape[0])
        for i, d in enumerate(data):
            small = ndimage.affine_transform(
                d, [self.medianZoom, self.medianZoom],
                output_shape=[d.shape[0] / self.medianZoom,
                              d.shape[1] / self.medianZoom])
            smallMedian = ndimage.median_filter(small, size=self.medianSize)
            median = ndimage.affine_transform(
                smallMedian, [1.0 / self.medianZoom, 1.0 / self.medianZoom],
                output_shape=d.shape, mode='nearest')
            interest[i] = median - d
            subscriber %= int(float(i + 1) / maxi * 70.0)
        hist = numpy.histogram(interest, range=(-255.0, 255.0), bins=511)
        width = numpy.sqrt(numpy.abs((hist[1][:-1] ** 2 * hist[0]).sum() \
                           / hist[0].sum()))
        self.threshold = self.significance * width
        self.binary = interest > self.threshold
        for i, b in enumerate(self.binary):
            self.binary[i] = ndimage.binary_fill_holes(b)
            self.binary[i] = ndimage.binary_opening(
                self.binary[i], iterations=1)
        subscriber %= 80


class AutoFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "AutoFocus"
    _sockets = [("zstack", Connectors.TYPE_IMAGE)]
    _params = [("medianSize", "median size", "(80, 80)", None),
               ("medianZoom", "median zoom", 8, None),
               ("significance", "feature significance", "3.0", None),
               ("areaThreshold", "area threshold in pixel", 4, None)]

    def autofocus(self, data, zsp, zsu, zind, inclusionList,
                  inclusionDict, lastLabelData):
        labelData = ndimage.label(zsp.binary[zind])[0]
        slicess = ndimage.find_objects(labelData)
        #previousMatchedStacks = {} # WTF?
        for label, slices in enumerate(slicess, start=1):
            slices = [slice(max(sli.start - 4, 0), sli.stop + 4) \
                      for sli in slices]
            dataDetail = data[slices].astype(float)
            footprint = labelData[slices] == label
            newInclusion = Inclusion(zind, label, slices, dataDetail,
                                     footprint, zsp, zsu)
            if not newInclusion.valid:
                labelData[slices] = numpy.where(footprint, 0, labelData[slices])
                continue
            inclusionList.append(newInclusion)
            inclusionDict[newInclusion.index] = newInclusion
            if lastLabelData is None:
                continue
            lastLabelDetail = numpy.where(footprint,
                                          lastLabelData[slices], 0)
            for l in numpy.unique(lastLabelDetail)[1:]:
                inclusionDict[(zind - 1, l)].append(newInclusion)
        return labelData

    @Worker.plug(Connectors.TYPE_ARRAY)
    def getStatistics(self, zstack, subscriber=0):
        # Initialization:
        longname = zstack.longname
        attributes = zstack.attributes
        data = zstack.data.astype(float)
        zsu = ZSUnits(zstack)
        del zstack
        labelData = None
        zsp = ZSParams(self)
        zsp.estimateThreshold(data, subscriber) # 80%
        inclusionList = []
        inclusionDict = {}
        # Calculate autofocus results:
        maxi = data.shape[0]
        for zid, sliceData in enumerate(data):
            labelData = self.autofocus(sliceData, zsp, zsu, zid, inclusionList,
                                       inclusionDict, labelData)
            subscriber %= 80 + int(float(zid) / float(maxi) * 10.0)
        # Extract statistics:
        inclusionList.sort(key=lambda x: x.focus, reverse=True)
        infoList = []
        base = numpy.zeros(data.shape[1:], dtype=bool)
        for inclusion in inclusionList:
            if not inclusion.valid:
                continue
            infoList.append(inclusion.getInfo(zsu))
            base[inclusion.fpSlices] |= inclusion.footprint
            inclusion.invalidateConnected()
        baseSum = float(base.sum())
        baseSize = float(base.size)
        baseArea = baseSize * zsu.amul * zsu.AQUANT
        projectedArea = baseSum * zsu.amul * zsu.AQUANT
        # Put info into SampleContainer:
        attributes = {'ZStackType':'StatisticsSC',
                      #'threshold':zsp.threshold,
                      #'ZStackAttributes':attributes,
                      'detectedInclusions':len(infoList),
                      'baseArea':baseArea,
                      'projectedArea':projectedArea}
        longname = 'Statistics_' + longname
        if len(infoList) == 0:
            return SampleContainer(longname=longname, columns=[],
                                   attributes=attributes)
        columnlns = ['zPos', 'yPos', 'xPos', 'diameter',
                     'focus', 'label', 'zIndex',
                     'ySliceStart', 'ySliceStop',
                     'xSliceStart', 'xSliceStop']
        columnsns = ['z', 'y', 'x', 'd', 'f', 'l',
                     'zi', 'yt', 'yp', 'xt', 'xp']
        from pyphant.core.Helpers import makeSC
        resultSC = makeSC(infoList, columnlns, columnsns,
                          longname, 's', attributes)
        subscriber %= 100
        return resultSC
