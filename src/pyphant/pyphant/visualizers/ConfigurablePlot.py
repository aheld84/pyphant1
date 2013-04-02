# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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


import matplotlib
import matplotlib.transforms
import wx

import copy
import pylab
import numpy
import pyphant.core.Connectors
from pyphant.core import DataContainer
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.quantities import isQuantity, Quantity
from pyphant.quantities.ParseQuantities import str2unit

class PlotPanel (wx.PyPanel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a
    flag, and the actual resizing of the figure is triggered by an Idle event."""
    def __init__( self, parent, color=None, dpi=None, **kwargs ):
        from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg,
                                                       NavigationToolbar2WxAgg)
        from matplotlib.figure import Figure

        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        self.parent = parent

        # initialize matplotlib stuff
        self.figure = Figure( None, dpi )
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(hspace=0.8)
        self.toolbar = NavigationToolbar2WxAgg(self.canvas)

        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        vSizer.Add(self.toolbar, 0, wx.EXPAND)
        self.draw()
        self.SetAutoLayout(True)
        self.SetSizer(vSizer)
        self.Layout()

    def draw(self):
        pass # abstract, to be overridden by child classes


class F(pylab.Formatter):
    def __init__(self, container, *args, **kwargs):
        self.container=container
    def __call__(self, x, pos=None):
        try:
            return str(x*self.container.unit)
        except IndexError, error:
            return str(x)


class OscPlotPanel(PlotPanel):
    x_key=0
    y_key=1
    c_key=2
    radius=Quantity('0.4mm')
    vmin = None
    vmax = None
    def __init__(self, parent, dataContainer):
        self.dataContainer = dataContainer
        PlotPanel.__init__(self, parent)

    def draw(self):
        self.x = self.dataContainer[self.x_key]
        self.y = self.dataContainer[self.y_key]
        self.c = self.dataContainer[self.c_key]
        if self.vmin is not None:
            self.vmin /= self.c.unit
        if self.vmax is not None:
            self.vmax /= self.c.unit
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(hspace=0.8)
        aspect = self.y.unit/self.x.unit
        if not isinstance(aspect, Quantity):
            self.ax.set_aspect(aspect)
        try:
            if self.c.mask!=None:
                mask = numpy.logical_not(self.c.mask)
                x = self.x.data[mask]
                y = self.y.data[mask]
                c = self.c.data[mask]
            else:
                x = self.x.data
                y = self.y.data
                c = self.c.data
            self.scat = self.ax.scatter(x,y,
                                        s=numpy.pi*(self.radius/self.x.unit)**2,
                                        c=c,
                                        vmin=self.vmin, vmax=self.vmax)
            self.colorbar = self.figure.colorbar(self.scat, format=F(self.c),
                                                 ax=self.ax)
            self.rescale(self.ax)
        except Exception, e:
            print e
        self.ax.set_xlabel(self.x.label)
        self.ax.set_ylabel(self.y.label)
        try:
            self.ax.set_title(self.dataContainer.attributes['title'])
        except KeyError,TypeError:
            pass
        self.ax.callbacks.connect('xlim_changed', self.rescale)
        self.ax.callbacks.connect('ylim_changed', self.rescale)
        self.canvas.draw()

    def rescale(self, ax):
        scale = self.ax.transData.get_affine().get_matrix().copy()
        scale[0,2]=0
        scale[1,2]=0
        scale[1,1]=scale[0,0]
        self.scat.set_transform(matplotlib.transforms.Affine2D(scale))


class ConfigurationPanel(wx.PyPanel):
    def __init__( self, parent, dataContainer, plot_panel):
        wx.Panel.__init__( self, parent)
        self.dataContainer = dataContainer
        self.plot_panel = plot_panel
        self.columns = [name for name in self.dataContainer.longnames.keys()
                        if isinstance(self.dataContainer[name],
                                      DataContainer.FieldContainer)]
        sizer = wx.FlexGridSizer(2, 6)
        sizer.Add(wx.StaticText(self, label="x axis: "))
        sizer.Add(wx.StaticText(self, label="y axis: "))
        sizer.Add(wx.StaticText(self, label="Color variable: "))
        sizer.Add(wx.StaticText(self, label="Minimal value: "))
        sizer.Add(wx.StaticText(self, label="Maximal value: "))
        sizer.Add(wx.StaticText(self, label="Radius: "))
        self.independentCombo = wx.ComboBox(self,
                                            style=wx.CB_READONLY | wx.CB_SORT,
                                            choices=self.columns)
        self.independentCombo.SetStringSelection(self.columns[0])
        longest = ''
        for s in self.columns:
            if len(s)>len(longest):
                longest = s
        offset = self.independentCombo.Size \
            - self.independentCombo.GetTextExtent(longest)
        maxSize = wx.Size(*self.independentCombo.GetTextExtent("White Reference Count somemore"))
        maxSize += offset
        self.independentCombo.MinSize = maxSize
        sizer.Add(self.independentCombo)
        self.dependentCombo = wx.ComboBox(self,
                                          style=wx.CB_READONLY | wx.CB_SORT,
                                          choices=self.columns)
        self.dependentCombo.SetStringSelection(self.columns[1])
        self.dependentCombo.MinSize = maxSize
        sizer.Add(self.dependentCombo)
        self.colorCombo = wx.ComboBox(self,
                                      style=wx.CB_READONLY | wx.CB_SORT,
                                      choices=self.columns)
        self.colorCombo.SetStringSelection(self.columns[2])
        self.colorCombo.MinSize = maxSize
        sizer.Add(self.colorCombo)
        self.vsize = wx.Size(*self.colorCombo.GetTextExtent('1234567890 nm')) + offset
        self.vmin_text = wx.TextCtrl(self, size=self.vsize,
                                     style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.vmin_text)
        self.vmax_text = wx.TextCtrl(self, size=self.vsize,
                                     style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.vmax_text)
        self.radius_text = wx.TextCtrl(self, size=self.vsize,
                                       style=wx.TE_PROCESS_ENTER)
        self.radius_text.Value = '0.4 mm'
        sizer.Add(self.radius_text)
        self.SetSizer(sizer)
        self.Centre()
        self.Bind(wx.EVT_COMBOBOX, self.changeColumns, self.independentCombo)
        self.Bind(wx.EVT_COMBOBOX, self.changeColumns, self.dependentCombo)
        self.Bind(wx.EVT_COMBOBOX, self.changeColumns, self.colorCombo)
        self.Bind(wx.EVT_TEXT_ENTER, self.changeColumns, self.vmin_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.changeColumns, self.vmax_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.changeColumns, self.radius_text)

    def changeColumns(self, event=None):
        independentVariable = self.independentCombo.GetValue()
        dependentVariable = self.dependentCombo.GetValue()
        colorVariable = self.colorCombo.GetValue()
        if (u''==independentVariable
            or u''==dependentVariable
            or u''==colorVariable):
            return
        self.plot_panel.x_key = independentVariable
        self.plot_panel.y_key = dependentVariable
        if self.plot_panel.c_key != colorVariable:
            self.plot_panel.c_key = colorVariable
            field = self.dataContainer[colorVariable]
            vmin = numpy.nanmin(field.data).round()*field.unit
            self.vmin_text.Value=str(vmin)
            vmax = numpy.nanmax(field.data).round()*field.unit
            self.vmax_text.Value=str(vmax)
        self.plot_panel.vmin = str2unit(self.vmin_text.Value)
        self.plot_panel.vmax = str2unit(self.vmax_text.Value)
        self.plot_panel.radius = str2unit(self.radius_text.Value)
        self.plot_panel.draw()
        self.GetSizer().Fit(self)

class PlotFrame(wx.Frame):
    name='Plot frame'
    def __init__(self, dataContainer, show=True):
        wx.Frame.__init__(self, None, -1, "Visualize "+dataContainer.longname)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.plot_panel = OscPlotPanel(self, dataContainer)
        self.configuration_panel = ConfigurationPanel(self, dataContainer,
                                                      self.plot_panel)
        self.sizer.Add(self.configuration_panel, 0, wx.EXPAND)
        self.sizer.Add(self.plot_panel, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Centre()
        self.Show(True)

    def createVisualizerList(self):
        ids={}
        if isinstance(self.dataContainer, DataContainer.SampleContainer):
            data_type = pyphant.core.Connectors.TYPE_ARRAY
        elif isinstance(self.dataContainer, DataContainer.FieldContainer):
            data_type = pyphant.core.Connectors.TYPE_IMAGE
        for visualizer in DataVisReg.getInstance().getVisualizers(data_type):
            id=wx.NewId()
            ids[id]=visualizer
            #self.GetCanvas().Bind(wx.EVT_MENU, self.visualize, id=id)
        return ids

    def OnExit(self, event):
        self.Close()




DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_ARRAY, PlotFrame)
