# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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
The ApplyMask Worker is a class of Pyphant's Image Processing
Toolbox. By using this worker one gry-scale image can be applied as a
mask on another image.  
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

#needed for constants defined in __init__.py
import ImageProcessing as IP
import scipy,copy

class ApplyMask(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name="Apply Mask"
    _sockets = [("image", Connectors.TYPE_IMAGE),("mask", Connectors.TYPE_IMAGE)]

    def check(self,image,mask):
        """Returns tupple of numpy arrays and checks their consistency."""
        for imD,mD in zip(image.dimensions,mask.dimensions):
            if not imD == mD:
                raise ValueError,'Dimension of input images has to be identical.'
        return image.data,mask.data

    @Worker.plug(Connectors.TYPE_IMAGE)
    def createMaskedImage(self, image, mask, subscriber=0):
        """Returns the masked input field."""
        img,m = self.check(image,mask)
        subscriber %= 10.

        result = scipy.where(m == IP.FEATURE_COLOR,img,IP.FEATURE_COLOR).astype('d')
        subscriber %= 55.0
        container = copy.deepcopy(image)
        container.data=result
        container.seal()
        subscriber %= 100.0

        return container

    @Worker.plug(Connectors.TYPE_ARRAY)
    def findMaskPoints(self, image, mask, subscriber=0):
        """Returns a table of masked points with each row giving a tupple (coordinate_1,...,coordindate_n,value)."""
        img,m = self.check(image,mask)
        subscriber %= 10.0

        index = (mask.data == IP.FEATURE_COLOR).nonzero()
        zVal      = image.data[index]
        subscriber %= 60.0

        fields = []
        for dim, coord in enumerate(index):
            newField = DataContainer.FieldContainer(image.dimensions[dim].data[coord],
                                image.dimensions[dim].unit,
                                longname=image.dimensions[dim].longname+" %i"%dim,
                                shortname=image.dimensions[dim].shortname)
            fields.append(newField)
        fields.append(DataContainer.FieldContainer(zVal, image.unit,
                                       longname=image.longname,
                                       shortname=image.shortname)
                     )
        res = DataContainer.SampleContainer(fields,
                                            u"Points from %s at %s"%(image.longname, mask.longname),
                                            u"X1")
        res.seal()
        subscriber %= 100.0
        return res


