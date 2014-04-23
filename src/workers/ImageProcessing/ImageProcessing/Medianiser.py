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
The Medianiser Worker is a class of Pyphant's Image Processing
Toolbox. It is used to remove noise from an image, by implementing a
standard median filter. In its configurations the size of the applied
kernel and the number of smoothing runs can be edited.
"""

from pyphant.core import (Worker, Connectors)
import scipy.ndimage.filters
import copy
import pkg_resources


class Medianiser(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Median"
    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("size", "Kernel Size", 5, None),
               ("runs", "Runs", 3, None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def medianize(self, field, subscriber=0):
        im = copy.deepcopy(field)
        size = self.paramSize.value
        ru = self.paramRuns.value
        for _ in xrange(ru):
            im.data = scipy.ndimage.filters.median_filter(im.data, size=size)
        im.seal()
        return im
