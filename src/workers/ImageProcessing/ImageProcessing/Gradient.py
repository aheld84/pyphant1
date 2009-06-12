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
Preliminary gradient worker
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer
import ImageProcessing
import numpy, copy

class Gradient(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Gradient"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    #_params = [("threshold", "Threshold", 160, None),
#               ("mode", "Mode(absolute/coverage)", ["absolute", "coverage"], None)
     #          ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def gradient(self, image, subscriber=0):
        #th=self.paramThreshold.value
        #resultArray = scipy.where( image.data < th,
        #                           ImageProcessing.FEATURE_COLOR,
        #                           ImageProcessing.BACKGROUND_COLOR )
        result = DataContainer.FieldContainer(
            sum(numpy.square(numpy.array(numpy.gradient(image.data)))),
            copy.deepcopy(image.unit), #TODO
            copy.deepcopy(image.error), #TODO
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            image.longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
