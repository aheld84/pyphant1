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
The Coverage Worker is a class of Pyphant's Image Processing
toolbox. It compares everx pixel with a calculated
threshold. Therefore required percentages of black and white material
in the image can be edited.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer

def weight2Coverage(w1, rho1, rho2):
    return (w1*rho2)/(w1*rho2+(1.0-w1)*rho1)

def calculateThreshold(image, coveragePercent):
    import scipy
    data = image.data
    histogram = scipy.histogram(data, len(scipy.unique(data)))
    cumsum = scipy.cumsum(histogram[0])
    targetValue = cumsum[-1]*coveragePercent
    index = scipy.argmin(scipy.absolute(cumsum-targetValue))
    threshold = histogram[1][index]
    return threshold*image.unit

class CoverageWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Coverage worker"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("w1", "Weight per cent of the dark material", "25%", None),
               ("rho1", "Density of the dark material", "0.97g/cm**3", None),
               ("rho2", "Density of the light material", "1.29g/cm**3", None),
               ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def threshold(self, image, subscriber=0):
        from pyphant.quantities.ParseQuantities import parseQuantity
        w1 = parseQuantity(self.paramW1.value)[0]
        rho1 = parseQuantity(self.paramRho1.value)[0]
        rho2 = parseQuantity(self.paramRho2.value)[0]
        coveragePercent = weight2Coverage(w1, rho1, rho2)
        th = calculateThreshold(image, coveragePercent)
        import scipy, ImageProcessing, copy
        resultArray = scipy.where( image.data < th,
                                   ImageProcessing.FEATURE_COLOR,
                                   ImageProcessing.BACKGROUND_COLOR )
        result = DataContainer.FieldContainer(resultArray,
                                              dimensions=copy.deepcopy(image.dimensions),
                                              longname=u"Binary Image", shortname=u"B")
        result.seal()
        return result


