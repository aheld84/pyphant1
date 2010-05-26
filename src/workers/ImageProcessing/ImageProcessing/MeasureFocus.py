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
from ImageProcessing.AutoFocus import FocusSlice

def sliceAndMeasure(image, labels, grow, human_output):
    from pyphant.core.KnowledgeManager import KnowledgeManager
    km = KnowledgeManager.getInstance()
    km.registerDataContainer(image)
    mask_parent = image.id
    data = image.data
    dy = (image.dimensions[0].data[1] - image.dimensions[0].data[0])
    dy *= image.dimensions[0].unit
    dx = (image.dimensions[1].data[1] - image.dimensions[1].data[0])
    dx *= image.dimensions[1].unit
    unit = image.unit / (dy * dx)
    slices = ndimage.find_objects(labels.data)
    if human_output:
        resdata = numpy.zeros(data.shape)
    else:
        resdata = numpy.zeros(len(slices), dtype=object)
    label = 0
    for sl in slices:
        label += 1
        if sl[0].stop - sl[0].start >= 3 and sl[1].stop - sl[1].start >= 3:
            start = [sl[0].start - grow, sl[1].start - grow]
            stop = [sl[0].stop + grow, sl[1].stop + grow]
            if start[0] < 0: start[0] = 0
            if start[1] < 0: start[1] = 0
            bigsl = (slice(start[0], stop[0]), slice(start[1], stop[1]))
            focus = numpy.sum(data[bigsl]) / data[bigsl].size
            if human_output:
                resdata[sl] = numpy.where(labels.data[sl] == label,
                                          focus, resdata[sl])
            else:
                #area = numpy.where(labels.data[sl] == label, 1, 0).sum()
                #area *= dx * dy
                mask = numpy.where(labels.data[sl] == label, True, False)
                dimslices = [slice(dim.data[subsl.start] * dim.unit,
                                   dim.data[subsl.stop - 1] * dim.unit + dl) \
                                 for subsl, dim, dl in zip(sl,
                                                           image.dimensions,
                                                           [dy, dx])]
                ydim = image.dimensions[0]
                xdim = image.dimensions[1]
                pixel_height = ydim.unit * (ydim.data[1] - ydim.data[0])
                pixel_width = xdim.unit * (xdim.data[1] - xdim.data[0])
                resdata[label - 1] = FocusSlice(dimslices, focus * unit,
                                                mask_parent, mask_slices=sl,
                                                pixel_width=pixel_width,
                                                pixel_height=pixel_height)
    longname = "MeasureFocus"
    if human_output:
        result = DataContainer.FieldContainer(resdata,
                                              unit,
                                              None,
                                              copy.deepcopy(image.mask),
                                              copy.deepcopy(image.dimensions),
                                              longname,
                                              image.shortname,
                                              copy.deepcopy(image.attributes),
                                              False)
    else:
        if len(slices) == 0:
            resdata = numpy.zeros(1, dtype=object)
        result = DataContainer.FieldContainer(data=resdata,
                                              longname=longname,
                                              shortname='F')
    return result


class MeasureFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "MeasureFocus"
    _sockets = [("image", Connectors.TYPE_IMAGE),
                ("labels", Connectors.TYPE_IMAGE)]
    _params = [("grow", "grow slices by #n pixels:", 3, None),
               ("humanOutput", "Human output", True, None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def measure_focus(self, image, labels, subscriber=0):
        result = sliceAndMeasure(image, labels,
                                 self.paramGrow.value,
                                 self.paramHumanOutput.value)
        result.seal()
        return result
