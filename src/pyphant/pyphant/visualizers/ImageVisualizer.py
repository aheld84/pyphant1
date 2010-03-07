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
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import pkg_resources
try:
    pkg_resources.require('matplotlib>=0.98.1')
    MPL_LT_0_98_1 = False
except:
    MPL_LT_0_98_1 = True

import pylab, scipy, numpy
from pyphant.core.Connectors import TYPE_IMAGE
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.quantities import isQuantity
#from NonUniformImage import NonUniformImage
from matplotlib.image import NonUniformImage

class F(pylab.Formatter):
    def __init__(self, container, *args, **kwargs):
        self.container=container
    def __call__(self, x, pos=None):
        try:
            return str(x*self.container.unit)#.replace('mu',r'\textmu{}')
        except IndexError, error:
            return str(x)

class ImageVisualizer(object):
    name='Image Visualizer'
    def __init__(self, fieldContainer,show=True):
        self.fieldContainer = fieldContainer
        self.show = show
        self.execute()

    def dataPrinter(self,event):
        x=self.fieldContainer.dimensions[-1]
        y=self.fieldContainer.dimensions[-2]
        zLabel=self.fieldContainer.shortname
        if event.inaxes:
            xc=event.xdata
            yc=event.ydata
            xi = numpy.abs(x.data-xc).argmin()
            yi = numpy.abs(y.data-yc).argmin()
            if ((self.fieldContainer.mask != None)
                and self.fieldContainer.mask[yi, xi]):
                val = "n/a"
            else:
                try:
                    val = self.fieldContainer.data[yi, xi]
                    val *= self.fieldContainer.unit
                except IndexError:
                    val = "nan"
            xval = xc * x.unit
            yval = yc * y.unit
            def format(val):
                if not isQuantity(val):
                    if type(val) in (type(' '),type(u' ')):
                        valstr = val
                    else:
                        valstr = "%.4g" % val
                else:
                    valstr = "%.3f %s" % (val.value,val.unit.name())
                return valstr
            labels = map(format,[xval,yval,val])
            labels.insert(0,zLabel)
            self.figure.canvas.toolbar.set_message("%s(%s,%s) = %s"
                                                   % tuple(labels))
        else:
            self.figure.canvas.toolbar.set_message("outside axis")

    def execute(self):
        pylab.ioff()
        self.figure = pylab.figure()
        self.figure.canvas.mpl_connect('motion_notify_event', self.dataPrinter)
        x = self.fieldContainer.dimensions[-1].data
        y = self.fieldContainer.dimensions[-2].data
        xmin=scipy.amin(x)
        xmax=scipy.amax(x)
        ymin=scipy.amin(y)
        ymax=scipy.amax(y)
        #Support for images with non uniform axes adapted
        #from python-matplotlib-doc/examples/pcolor_nonuniform.py
        ax = self.figure.add_subplot(111)
        vmin = self.fieldContainer.attributes.get('vmin', None)
        vmax = self.fieldContainer.attributes.get('vmax', None)
        if vmin is not None:
            vmin /= self.fieldContainer.unit
        if vmax is not None:
            vmax /= self.fieldContainer.unit
        if MPL_LT_0_98_1 or self.fieldContainer.isLinearlyDiscretised():
            pylab.imshow(self.fieldContainer.maskedData,
                         aspect='auto',
                         interpolation='nearest',
                         vmin=vmin,
                         vmax=vmax,
                         origin='lower',
                         extent=(xmin, xmax, ymin, ymax))
            pylab.colorbar(format=F(self.fieldContainer), ax=ax)
        else:
            im = NonUniformImage(ax, extent=(xmin,xmax,ymin,ymax))
            if vmin is not None or vmax is not None:
                im.set_clim(vmin, vmax)
                im.set_data(x, y, self.fieldContainer.maskedData)
            else:
                im.set_data(x, y, self.fieldContainer.maskedData)
                im.autoscale_None()
            ax.images.append(im)
            ax.set_xlim(xmin,xmax)
            ax.set_ylim(ymin,ymax)
            pylab.colorbar(im,format=F(self.fieldContainer), ax=ax)
        pylab.xlabel(self.fieldContainer.dimensions[-1].shortlabel)
        pylab.ylabel(self.fieldContainer.dimensions[-2].shortlabel)
        pylab.title(self.fieldContainer.label)
        #ax=pylab.gca()
        if self.show:
            pylab.ion()
            pylab.show()


DataVisReg.getInstance().registerVisualizer(TYPE_IMAGE, ImageVisualizer)
