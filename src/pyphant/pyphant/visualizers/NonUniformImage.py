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

from matplotlib.image import AxesImage
import numpy as np
from numpy import ma
from matplotlib import _image, colors as mcolors

class NonUniformImage(AxesImage):
    def __init__(self, ax,
                 **kwargs
                ):
        AxesImage.__init__(self, ax,
                           **kwargs)

    def make_image(self, magnification=1.0):
        if self._A is None:
            raise RuntimeError('You must first set the image array')

        x0, y0, v_width, v_height = self.axes.viewLim.bounds
        l, b, r, t = self.axes.bbox.extents
        width = (round(r) + 0.5) - (round(l) - 0.5)
        height = (round(t) + 0.5) - (round(b) - 0.5)
        width *= magnification
        height *= magnification
        im = _image.pcolor(self._Ax, self._Ay, self._A,
                           height, width,
                           (x0, x0+v_width, y0, y0+v_height))
        fc = self.axes.get_frame().get_facecolor()
        bg = mcolors.colorConverter.to_rgba(fc, 0)
        im.set_bg(*bg)
        return im

    def set_data(self, x, y, A):
        x = np.asarray(x,np.float32)
        y = np.asarray(y,np.float32)
        A = ma.asarray(A)
        if len(x.shape) != 1 or len(y.shape) != 1\
           or A.shape[0:2] != (y.shape[0], x.shape[0]):
            raise TypeError("Axes don't match array shape")
        if len(A.shape) not in [2, 3]:
            raise TypeError("Can only plot 2D or 3D data")
        if len(A.shape) == 3 and A.shape[2] not in [1, 3, 4]:
            raise TypeError("3D arrays must have three (RGB) or four (RGBA) color components")
        if len(A.shape) == 3 and A.shape[2] == 1:
            A.shape = A.shape[0:2]
        if len(A.shape) == 2:
            if A.dtype != np.uint8:
                A = (self.cmap(self.norm(A))*255).astype(np.uint8)
            else:
                A = np.repeat(A[:,:,np.newaxis], 4, 2)
                A[:,:,3] = 255
        else:
            if A.dtype != np.uint8:
                A = (255*A).astype(np.uint8)
            if A.shape[2] == 3:
                B = zeros(tuple(list(A.shape[0:2]) + [4]), np.uint8)
                B[:,:,0:3] = A
                B[:,:,3] = 255
                A = B
        self._A = A
        self._Ax = x
        self._Ay = y
        self._imcache = None

    def set_array(self, *args):
        raise NotImplementedError('Method not supported')

    def set_interpolation(self, s):
        if s != None and s != 'nearest':
            raise NotImplementedError('Only nearest neighbor supported')
        AxesImage.set_interpolation(self, s)

    def get_extent(self):
        if self._A is None:
            raise RuntimeError('Must set data first')
        return self._Ax[0], self._Ax[-1], self._Ay[0], self._Ay[-1]

    def set_filternorm(self, s):
        pass

    def set_filterrad(self, s):
        pass

    def set_norm(self, norm):
        if self._A is not None:
            raise RuntimeError('Cannot change colors after loading data')
        cm.ScalarMappable.set_norm(self, norm)

    def set_cmap(self, cmap):
        if self._A is not None:
            raise RuntimeError('Cannot change colors after loading data')
        cm.ScalarMappable.set_cmap(self, norm)

