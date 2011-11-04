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
The Thresholding Worker is a class of Pyphant's Image Processing
Toolbox. The threshold can be edited in the worker's configuration. It
returns a binary image where pixels that comprise features are set to
0x00 whereas background pixels are set to 0xFF.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, DataContainer)
import ImageProcessing
import scipy
import copy


class ThresholdingWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Threshold"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _params = [("threshold", "Threshold", "160.0", None),
               ("unit", "Unit", "ignore", None)
#               ("mode", "Mode(absolute/coverage)",
#                ["absolute", "coverage"], None)
               ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def threshold(self, image, subscriber=0):
        th = float(self.paramThreshold.value)
        if self.paramUnit.value.lower() != 'ignore':
            from pyphant.quantities import Quantity, isQuantity
            try:
                unit = float(self.paramUnit.value)
                assert not isQuantity(image.unit)
            except ValueError:
                try:
                    unit = Quantity(self.paramUnit.value)
                except TypeError:
                    unit = Quantity(1.0, self.paramUnit.value)
                assert isQuantity(image.unit)
                assert unit.isCompatible(image.unit.unit)
            th *= unit / image.unit
        resultArray = scipy.where(image.data < th,
                                  ImageProcessing.FEATURE_COLOR,
                                  ImageProcessing.BACKGROUND_COLOR)
        result = DataContainer.FieldContainer(resultArray,
                                    dimensions=copy.deepcopy(image.dimensions),
                                    longname=u"Binary Image", shortname=u"B")
        result.seal()
        return result
