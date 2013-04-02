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


from pyphant.core import Worker, Connectors,\
                         Param, DataContainer

from scipy import zeros,amax,add,floor,rand
import numpy
import copy

#needed for constants defined in __init__.py
import ImageProcessing as IP

BC = IP.BACKGROUND_COLOR
FC = IP.FEATURE_COLOR
corner = numpy.array([[BC,BC,BC],[FC,FC,BC],[FC,FC,BC]])
corners = map(lambda i: numpy.rot90(corner,k=i), range(4))

class SkeletonizeFeature(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Skeletonize"
    _sockets = [ ("image", Connectors.TYPE_IMAGE)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def execute(self, image, subscriber=0):
        skeleton = skeletonize(image.data,subscriber)
        result = DataContainer.FieldContainer(skeleton,
                        dimensions=copy.deepcopy(image.dimensions),
                        unit = image.unit,
                        longname=u"Binary Image", shortname=u"B")
        result.seal()
        return result


def checkNeighbours(data):
    """Checks the neighboured pixel of data[1,1] and returns a fingerprint (N_f,N_b,N_t) with
N_f: Number of neighboured pixels which are features,
N_b: Number of close neighboure pixels which belong to the background,
N_c: Corner Position, or -1 if no corner."""
    features = 0
    background = 0
    neighbours = [data[0,0],data[0,1],data[0,2],data[1,2],data[2,2],data[2,1],data[2,0],data[1,0]]
    fourConnected = False
    lastPoint = neighbours[-1] #Needed for checking a complete transition cycle
    for n in neighbours:
        if not n:
            features += 1
        elif fourConnected:
            background += 1

        fourConnected = not fourConnected
        lastPoint = n

    for pos,corner in enumerate(corners):
        if numpy.alltrue(data == corner):
            cornerPos = pos+1
            break
        else:
            cornerPos = 0
    return (features,background,cornerPos)

def checkTransitions(data):
    """Checks the neighboured pixel of data[1,1] and returns the
    N_f: Number of transitions from feature pixels to background pixels counted in clockwise order."""
    transitions = 0
    neighbours = [data[0,0],data[0,1],data[0,2],data[1,2],data[2,2],data[2,1],data[2,0],data[1,0]]
    lastPoint = neighbours[-1] #Needed for checking a complete transition cycle
    for n in neighbours:
        if not lastPoint and n:
            transitions += 1
        lastPoint = n
    return transitions

def skeletonize(data,subscriber = 0):
    """Computes the skeleton of a binary image. The algorithm is an enhanced
    version of the receipe described by Steven W. Smith in his 'The Scientist
    and Engineer's Guide to Digital Signal Processing' (www.dspguide.com/ch25/4.htm).
    It is applied to a zero padded copy of the input data. Therefore pixels of the
    feature are removed iteratively while the following rules apply:
    Rule I   : The pixel is a feature.
    Rule II  : At least one of the pixels closests neighbours belongs to the background.
    Rule III : More than one of the neighboured pixels belong to a feature.
    Rule IV  : If the neighboured pixels are considered clockwise, only one transition from feature to background pixels occurs.
    Rule V   : The pixel was not located diagonally to a corner feature pixel in the previous iteration.
"""
    nx,ny=data.shape
    #zero padding
    image = zeros((nx+2,ny+2),'int16')
    image[:,:] = IP.BACKGROUND_COLOR
    image[1:-1,1:-1]=data

    erosionComplete = False
    runs = 0
    erosionComplete = False
    runs = 0
    isCorner = zeros((nx+2,ny+2),'bool')
    while not erosionComplete:
        ruleI   = (image == IP.FEATURE_COLOR)
        XFeat, YFeat = ruleI.nonzero()
        numberFeatures = len(XFeat)
        erosedPixels = 0
        if runs == 0:
            progressbar = progress(numberFeatures)
        neighbourhood = zeros((nx+2,ny+2,3),'int16')
        for x,y in zip(XFeat.tolist(),YFeat.tolist()):
            fingerprint = checkNeighbours(image[x-1:x+2,y-1:y+2])
            neighbourhood[x,y,:]=numpy.array(fingerprint)

        ruleII  = neighbourhood[:,:,1]>=1
        ruleIII = neighbourhood[:,:,0]> 1
        border = (ruleI & ruleII & ruleIII)
        #ruleIV and ruleV
        XBord, YBord = border.nonzero()
        XBord2 = []
        YBord2 = []
        for x,y in zip(XBord.tolist(),YBord.tolist()):
            if checkTransitions(image[x-1:x+2,y-1:y+2]) <= 1 and not isCorner[x,y]:
                image[x,y] = IP.BACKGROUND_COLOR
                erosedPixels += 1
                subscriber %= progressbar.step()
            else:
                XBord2.append(x)
                YBord2.append(y)
        for x,y in zip(XBord2,YBord2):
            if checkTransitions(image[x-1:x+2,y-1:y+2]) <= 1 and not isCorner[x,y]:
                image[x,y] = IP.BACKGROUND_COLOR
                erosedPixels += 1
                subscriber %= progressbar.step()
        if erosedPixels == 0:
            erosionComplete = True
            subscriber %= 100.
        else:
            xCorn, yCorn = (neighbourhood[:,:,2] > 0 ).nonzero()
            for x,y in zip(xCorn.tolist(),yCorn.tolist()):
                if neighbourhood[x,y,2] == 1:
                    isCorner[x+1,y-1] = True
                elif neighbourhood[x,y,2] == 2:
                    isCorner[x+1,y+1] = True
                elif neighbourhood[x,y,2] == 3:
                    isCorner[x-1,y+1] = True
                elif neighbourhood[x,y,2] == 4:
                    isCorner[x-1,y-1] = True
        runs += 1
    return image[1:-1,1:-1].copy()


class progress:
    def __init__(self,initialFeatures):
        self.features = initialFeatures
        #The more features we have, the less will one iteration achieve
        self.delta = 100.0/self.features
        self.status = 0.0
        self.first = True

    def step(self):
        self.status += self.delta
        return self.status



