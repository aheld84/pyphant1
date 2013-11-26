# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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
The Load Image worker is a class of Pyphant's Image Processing
Toolbox. It simply loads an image from the location given in the
worker's configuration.
"""

from pyphant.core import (Worker, Connectors, DataContainer)
import pkg_resources
import PIL.Image
import scipy
import scipy.misc
from pyphant.core.Helpers import parseFCUnit


class ImageLoaderWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Load Image"
    _params = [("filename", u"Filename", "", Connectors.SUBTYPE_FILE),
               ("fieldUnit", u"Unit of the field", "1", None),
               ("xScale", u"Scale of the x-axis (eg. 100nm)", '1mum', None),
               ("yScale", u"Scale of the y-axis (eg. 100nm)", 'link2X', None)]

## Result is colour image
##     @Worker.plug(Connectors.TYPE_IMAGE)
##     def loadImage(self, subscriber=0):
##         im=PIL.Image.open(self.paramFilename.value)
##         im.load()
##         size=im.size
##         print scipy.fromimage(im).shape
##         result = DataContainer.FieldContainer(scipy.fromimage(im),
##                       Quantity(self.paramFieldUnit.value, 'mum'))
##         result.dimensions[0].unit = Quantity(1. / float(size[0]),
##                                                    self.paramXUnit.value)
##         result.dimensions[1].unit = Quantity(1. / float(size[1]),
##                                                    self.paramYUnit.value)
##         return result

    def _getScalar(self, fc_unit):
        try:
            return fc_unit.value
        except AttributeError:
            return fc_unit

    @Worker.plug(Connectors.TYPE_IMAGE)
    def loadImageAsGreyScale(self, subscriber=0):
        im = PIL.Image.open(self.paramFilename.value)
        if im.mode == "I;16":
            im = im.convert("I")
            data = scipy.misc.fromimage(im).astype("int16")
        else:
            data = scipy.misc.fromimage(im, flatten=True)
        Ny, Nx = data.shape
        xUnit = parseFCUnit(self.paramXScale.value)
        xAxis = DataContainer.FieldContainer(
            scipy.linspace(0.0, self._getScalar(xUnit), Nx, True),
            xUnit / self._getScalar(xUnit),
            longname='x-coordinate',
            shortname='x'
            )
        if self.paramYScale.value == 'link2X':
            yUnit = xUnit * float(Ny) / Nx
        else:
            yUnit = parseFCUnit(self.paramYScale.value)
        yAxis = DataContainer.FieldContainer(
            scipy.linspace(0.0, self._getScalar(yUnit), Ny, True),
            yUnit / self._getScalar(yUnit),
            longname='y-coordinate',
            shortname='y'
            )
        fieldUnit = parseFCUnit(self.paramFieldUnit.value)
        result = DataContainer.FieldContainer(
            data,
            fieldUnit,
            longname="Image",
            shortname="I",
            dimensions=[yAxis, xAxis]
            )
        result.seal()
        return result
