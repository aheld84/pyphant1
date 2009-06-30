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
from scipy import ndimage
from ImageProcessing.NDImageWorker import pile

class MeasureFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "MeasureFocus"
    _sockets = [("image", Connectors.TYPE_IMAGE),
                ("labels", Connectors.TYPE_IMAGE)]
    _params = [("grow", "grow slices by #n pixels:", 3, None)]

    def getFocus(self, data):
        #return numpy.sum(numpy.sqrt(numpy.sum(numpy.square(
        #                numpy.array(numpy.gradient(data)))))) / data.size
        return numpy.sum(data) / data.size

    def sliceAndMeasure(self, data):
        grow = self.paramGrow.value
        slices = ndimage.find_objects(self._labels)
        res = numpy.zeros(data.shape)
        label = 0
        for sl in slices:
            label += 1
            if sl[0].stop - sl[0].start >= 3 and sl[1].stop - sl[1].start >= 3:
                start = [sl[0].start - grow, sl[1].start - grow]
                stop = [sl[0].stop + grow, sl[1].stop + grow]
                if start[0] < 0: start[0] = 0
                if start[1] < 0: start[1] = 0
                bigsl = (slice(start[0], stop[0]), slice(start[1], stop[1]))
                focus = self.getFocus(data[bigsl])
                res[sl] = numpy.where(self._labels[sl] == label, focus, res[sl])
        return res

    @Worker.plug(Connectors.TYPE_IMAGE)
    def measure_focus(self, image, labels, subscriber=0):
        self._labels = labels.data
        newdata = pile(self.sliceAndMeasure, image.data)
        longname = "MeasureFocus"
        result = DataContainer.FieldContainer(
            newdata,
            copy.deepcopy(image.unit),
            copy.deepcopy(image.error),
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
