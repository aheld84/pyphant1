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

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import scipy
import wx
from enthought.chaco2 import api as chaco2
from enthought.chaco2.tools import api as tools
from enthought.enable2.wx_backend import Window
from pyphant.core.Connectors import TYPE_IMAGE
from enthought.chaco2.default_colormaps \
     import color_map_name_dict

class PlotFrame(wx.Frame):
    name = 'New Image Visualizer'
    def __init__(self, fieldContainer, *args, **kw):
        kw["size"] = (600,600)
        wx.Frame.__init__(*(self,None,)+args, **kw)
        data = chaco2.ArrayPlotData()
        data.set_data('imagedata', fieldContainer.data.data)
        plot = chaco2.Plot(data)
        plot.img_plot('imagedata',
                      xbounds=fieldContainer.dimensions[0].data,
                      ybounds=fieldContainer.dimensions[1].data,
                      colormap = color_map_name_dict['jet'])
        plot.overlays.append(tools.SimpleZoom(plot, tool_mode="box", always_on=True))
        self.plot_window = Window(parent=self, component=plot)
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return

## class ImageVisualizer(object):
##     name='Image Visualizer'
##     def __init__(self, fieldContainer):
##         self.fieldContainer = fieldContainer
##         self.execute()
    
##     def execute(self):
##         pylab.ioff()
##         self.figure = pylab.figure()
##         xmin=scipy.amin(self.fieldContainer.dimensions[0].data)
##         xmax=scipy.amax(self.fieldContainer.dimensions[0].data)
##         ymin=scipy.amin(self.fieldContainer.dimensions[1].data)
##         ymax=scipy.amax(self.fieldContainer.dimensions[1].data)

##         pylab.imshow(self.fieldContainer.data, extent=(xmin, xmax, ymin, ymax))
##         pylab.xlabel(self.fieldContainer.dimensions[0].label)
##         pylab.ylabel(self.fieldContainer.dimensions[1].label)
##         pylab.title(self.fieldContainer.longname)

##         class F(pylab.Formatter):
##             def __init__(self, container, *args, **kwargs):
##                 self.container=container
##             def __call__(self, x, pos=None):
##                 try: 
##                     return str(x*self.container.unit).replace('mu',r'\textmu{}')
##                 except IndexError, error:
##                     return str(x)
##         ax=pylab.gca()
##         pylab.colorbar(format=F(self.fieldContainer))
##         pylab.ion()
##         pylab.show()


