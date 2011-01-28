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
The ImageLoader Worker is a class of Pyphant's Image Processing
Toolbox. It simply loads an image from the location given in the
worker's configuration.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import PIL.Image as Image
import scipy
from pyphant import quantities

from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)


class ImageLoaderWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Load Image"
##     lengthUnits=[prefix[0]+'m' for prefix
##                  in quantities._prefixes if prefix[1]>1]
##     lengthUnits.append('m')
##     lengthUnits+=[prefix[0]+'m' for prefix
##                   in quantities._prefixes if prefix[1]<1]

    _params=[("filename", u"Filename", "", Connectors.SUBTYPE_FILE),
             ("fieldUnit", u"Unit of the field", 1, None),
             ("xScale", u"Scale of the x-axis (eg. 100nm)", '1mum', None),
             ("yScale", u"Scale of the y-axis (eg. 100nm)", 'link2X', None)]

## Result is colour image
##     @Worker.plug(Connectors.TYPE_IMAGE)
##     def loadImage(self, subscriber=0):
##         im=Image.open(self.paramFilename.value)
##         im.load()
##         size=im.size
##         print scipy.fromimage(im).shape
##         result = DataContainer.FieldContainer(scipy.fromimage(im),
##                                               quantities.Quantity(self.paramFieldUnit.value, 'mum'))
##         result.dimensions[0].unit=quantities.Quantity(1./float(size[0]), self.paramXUnit.value)
##         result.dimensions[1].unit=quantities.Quantity(1./float(size[1]), self.paramYUnit.value)
##         return result

    @Worker.plug(Connectors.TYPE_IMAGE)
    def loadImageAsGreyScale(self, subscriber=0):
        im=Image.open(self.paramFilename.value)
        if im.mode == "I;16":
            im = im.convert("I")
            data = scipy.misc.fromimage(im).astype("int16")
        else:
            data = scipy.misc.fromimage(im, flatten=True)
        Ny, Nx = data.shape
        xUnit = quantities.Quantity(self.paramXScale.value.encode('utf-8'))
        xAxis =  DataContainer.FieldContainer(scipy.linspace(0.0,xUnit.value,Nx,True),
                                              xUnit / xUnit.value,
                                              longname = 'x-coordinate',
                                              shortname = 'x')
        if self.paramYScale.value == 'link2X':
            yUnit = xUnit * float(Ny) / Nx
        else:
            yUnit = quantities.Quantity(self.paramYScale.value.encode('utf-8'))
        yAxis =  DataContainer.FieldContainer(scipy.linspace(0.0,yUnit.value,Ny,True),
                                              yUnit / yUnit.value,
                                              longname = 'y-coordinate',
                                              shortname = 'y')
        try:
            FieldUnit = quantities.Quantity(self.paramFieldUnit.value.encode('utf-8'))
        except AttributeError:
            FieldUnit = self.paramFieldUnit.value
        result = DataContainer.FieldContainer(data,
                                              FieldUnit,
                                              longname="Image",
                                              shortname="I",
                                              dimensions=[yAxis, xAxis])
        result.seal()
        return result


