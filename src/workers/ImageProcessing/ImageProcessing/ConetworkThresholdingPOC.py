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
"""


import Image
from scipy import *
from pylab import *

def getCovering():
    wt = 0.25
    PDMS=970 #feature mass density [mg/ml]
    PHEA=1290 # background mass density [mg/ml]","BackgroundRho

    covering = wt * PHEA / (wt * PHEA + (1.0-wt)*PDMS)
    return covering

def threshold(self, image, subscriber=0):
    th=self.paramThreshold.value
    resultArray = scipy.where( image.data < th,
                               ImageProcessing.FEATURE_COLOR,
                               ImageProcessing.BACKGROUND_COLOR )
    result = DataContainer.FieldContainer(resultArray,
                                          dimensions=copy.deepcopy(image.dimensions),
                                          longname=u"Binary Image", shortname=u"B")
    result.seal()
    return result

im = Image.open('../../../../0.3/trunk/doc/fig/SG-ScaleUp/nb216a-8a.jpg')
field = fromimage(im,flatten=True)
print "Covering",getCovering()
print amin(amin(field)),amax(amax(field))
field1D = resize(field,(size(field),))
h = stats.histogram(field1D,numbins=255,defaultlimits=(0,255))

prob = interpolate.interp1d(arange(1,256),1.0*cumsum(h[0])/size(field)-getCovering())
print prob(80)
threshold = optimize.bisect(prob,1.0,255.0)
print "Threshold",threshold
#plot(prob(arange(1,256)))

binary = where( field < threshold,0,255)
imshow(binary)
show()
