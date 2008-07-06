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
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors,
                          DataContainer)

import scipy

class UltimatePointsCalculator(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Ultimate points calculator"
    _sockets = [("image", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def findUltimatePoints(self, image, subscriber=0):
        img=image.data
        nx,ny=img.shape
        ultimatePoints=[]
        #corners:
        if img[0,0]==scipy.amax(scipy.amax(img[:2,:2])):
            ultimatePoints.append((0,0,img[0,0]))
        if img[0,ny-1]==scipy.amax(scipy.amax(img[:2,ny-2:])):
            ultimatePoints.append((0,ny-1,img[0,ny-1]))
        if img[nx-1,0]==scipy.amax(scipy.amax(img[nx-2:,:2])):
            ultimatePoints.append((nx-1,0,img[nx-1,0]))
        if img[nx-1,ny-1]==scipy.amax(scipy.amax(img[nx-2:,ny-2:])):
            ultimatePoints.append((nx-1,ny-1,img[nx-1,ny-1]))
        #upper edge:
        for x in xrange(1,nx-1):
            if img[x,0]==scipy.amax(scipy.amax(img[x-1:x+2,:2])):
                ultimatePoints.append((x,0,img[x,0]))
        #lower edge:
        for x in xrange(1,nx-1):
            if img[x,ny-1]==scipy.amax(scipy.amax(img[x-1:x+2,ny-2:])):
                ultimatePoints.append((x,ny-1,img[x,ny-1]))
        #left edge:
        for y in xrange(1,ny-1):
            if img[0,y]==scipy.amax(scipy.amax(img[:2,y-1:y+2])):
                ultimatePoints.append((0,y,img[0,y]))
        #right edge:
        for y in xrange(1,ny-1):
            if img[nx-1,y]==scipy.amax(scipy.amax(img[nx-2:,y-1:y+2])):
                ultimatePoints.append((nx-1,y,img[nx-1,y]))
        #inner image:
        for y in xrange(1,ny-1):
            for x in xrange(1,nx-1):
                if img[x,y]==scipy.amax(scipy.amax(img[x-1:x+2,y-1:y+2])):
                    ultimatePoints.append((x,y,img[x,y]))

        ultimatePoints=scipy.array(filter(lambda (x,y,v): v>0, ultimatePoints))
        x=DataContainer.FieldContainer(ultimatePoints[:,0], image.dimensions[0].unit,
                                       longname=image.dimensions[0].longname,
                                       shortname=image.dimensions[0].shortname)
        y=DataContainer.FieldContainer(ultimatePoints[:,1], image.dimensions[1].unit,
                                       longname=image.dimensions[1].longname,
                                       shortname=image.dimensions[1].shortname)
##         z=DataContainer.FieldContainer(ultimatePoints[:,2], scipy.sqrt(image.dimensions[0].unit**2
##                                                                        +image.dimensions[1].unit**2),
##                                        longname=u"Distance to background",
##                                        shortname=u"d")
        z=DataContainer.FieldContainer(ultimatePoints[:,2], image.unit,
                                       longname=u"Distance to background",
                                       shortname=u"d")
        x.seal()
        y.seal()
        z.seal()

        return DataContainer.SampleContainer([x,y,z],
                                             u"Ultimate points from %s"%(image.longname,),
                                             u"D")


