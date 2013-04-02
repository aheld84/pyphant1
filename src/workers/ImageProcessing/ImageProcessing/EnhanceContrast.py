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
Deprecated
"""


from pyphant.core import (Worker, Connectors, DataContainer)
import scipy, copy
import pkg_resources

def normalizeHistogram(data):
    histogram = scipy.ndimage.histogram(data.astype("f"), 0, 255, 256)
    cumulatedHistogram = scipy.cumsum(histogram)
    nch = cumulatedHistogram.astype("f")/len(data.flat)
    inch = (nch*255).astype("i")
    normalize = scipy.vectorize(lambda i: inch[i])
    return normalize(data)
    #return data

def normalizeLinear(data):
    res = data - data.min()
    res = (res * 255) / res.max()
    return res

class EnhanceContrast(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Enhance Contrast"
    _sockets = [("image", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def enhance(self, image, subscriber=0):
        newdata = normalizeLinear(image.data)
        longname = "Normalize"
        result = DataContainer.FieldContainer(
            newdata,
            1,
            None,
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
