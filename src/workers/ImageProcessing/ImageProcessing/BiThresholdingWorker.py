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
"""

__id__ = "$Id: ThresholdingWorker.py 20 2006-11-21 18:17:23Z liehr $"
__author__ = "$Author: liehr $"
__version__ = "$Revision: 20 $"
# $Source$

from pyphant.core import (Worker, Connectors, DataContainer)
import ImageProcessing
import scipy
import copy


class BiThresholdingWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision: 20 $"[11:-1]
    name = "Bi-Thresholdfilter"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("lowerThreshold", "lower threshold", 125, None),
               ("upperThreshold", "upper threshold", 180, None)]
    lowerImage = None
    lowerThreshold = None
    upperImage = None
    upperThreshold = None
    intermediateImage = None

    def getBinary(self, image, threshold):
        binaryImage = scipy.where(image.data < threshold,
                                  ImageProcessing.FEATURE_COLOR,
                                  ImageProcessing.BACKGROUND_COLOR)
        return binaryImage

    def computeCovering(self, data):
        nx, ny = data.shape
        count = 0
        for x in xrange(0, nx):
            for y in xrange(0, ny):
                if data[x, y] == 0:
                    count += 1
        covering = float(count) / (nx * ny)
        return covering

    def getLowerImage(self, image):
        if self.lowerImage == None or\
                self.lowerThreshold != self.paramLowerThreshold.value:
            self.lowerThreshold = self.paramLowerThreshold.value
            self.lowerImage = self.getBinary(image, self.lowerThreshold)
        return self.lowerImage

    def getUpperImage(self, image):
        if self.upperImage == None or\
            self.upperThreshold != self.paramUpperThreshold.value:
            self.upperThreshold = self.paramUpperThreshold.value
            self.upperImage = self.getBinary(image, self.upperThreshold)
        return self.upperImage

    def getIntermediate(self, image):
        if self.intermediateImage == None:
            lowerImage = self.getLowerImage(image)
            upperImage = self.getUpperImage(image)
            intermediateArray = scipy.absolute(lowerImage - upperImage)
            max = scipy.amax(intermediateArray)
            min = scipy.amin(intermediateArray)
            self.intermediateImage = max + min - intermediateArray
        return self.intermediateImage

    @Worker.plug(Connectors.TYPE_IMAGE)
    def threshold(self, image, subscriber=0):
        data = self.getIntermediate(image)
        result = DataContainer.FieldContainer(data,
                                dimensions=copy.deepcopy(image.dimensions),
                                longname=u"Binary Image", shortname=u"B")
        result.seal()
        return result

    def getCovering(self, image):
        lower = self.computeCovering(self.getLowerImage(image))
        intermediate = self.computeCovering(self.getIntermediate(image))
        upper = 1.0 - lower - intermediate

        return 100.0 * scipy.array([lower, intermediate, upper])

    @Worker.plug(Connectors.TYPE_IMAGE)
    def covering(self, image, subscriber=0):
        lowerThreshold = self.paramLowerThreshold.value
        upperThreshold = self.paramUpperThreshold.value
        lowerCover, intermediateCover, upperCover = self.getCovering(image)
        data = image.data.copy()
        nx, ny = data.shape
        for x in xrange(0, nx):
            for y in xrange(0, ny):
                if data[x, y] < upperThreshold:
                    if data[x, y] < lowerThreshold:
                        data[x, y] = lowerCover
                    else:
                        data[x, y] = intermediateCover
                else:
                    data[x, y] = upperCover
        covering = self.getCovering(image)
        print covering
        result = DataContainer.FieldContainer(data,
                                    dimensions=copy.deepcopy(image.dimensions),
                                    longname=u"Covering Image %s" % covering,
                                    shortname=u"C")
        result.seal()
        return result

    @Worker.plug(Connectors.TYPE_ARRAY)
    def documentCovering(self, image,subscriber=0):
        thresholds = scipy.array([self.paramLowerThreshold.value,
                                  self.paramUpperThreshold.value,
                                  scipy.amax(image.data)])
        coveringVec = self.getCovering(image)
        theta = DataContainer.FieldContainer(thresholds, '1',
                                        longname='Value of upper threshold',
                                        shortname='\theta')
        A = DataContainer.FieldContainer(coveringVec, '1',
                                         longname='Covering', shortname='A')
        print theta.data, thresholds
        print A.data, coveringVec
        res = DataContainer.SampleContainer([theta, A],
                                            u"Covering of image parts", u"X_A")
        res.seal()
        return res
