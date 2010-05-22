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

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import matplotlib
import wx

import copy
import pylab
import numpy
import pyphant.core.Connectors
from pyphant.core import DataContainer
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.quantities import isQuantity, Quantity


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
    def __init__(self, parent, dataContainer):
        self.dataContainer = dataContainer
        PlotPanel.__init__(self, parent)

    def draw(self):
        x = self.dataContainer[self.x_key]
        y = self.dataContainer[self.y_key]
        c = self.dataContainer[self.c_key]
        vmin = None
        vmax = None
        if vmin is not None:
            vmin /= c.unit
        if vmax is not None:
            vmax /= c.unit
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(hspace=0.8)
        try:
            scat = self.ax.scatter(x.data, y.data, c=c.data, vmin=vmin, vmax=vmax)
            self.figure.colorbar(scat, format=F(c), ax=self.ax)
        except:
            pass
        self.ax.set_xlabel(x.label)
        self.ax.set_ylabel(y.label)
        try:
            self.ax.set_title(self.dataContainer.attributes['title'])
        except KeyError,TypeError:
            pass
        self.canvas.draw()

class ConfigurationPanel(wx.PyPanel):
    def __init__( self, parent, dataContainer, plot_panel):
        wx.Panel.__init__( self, parent)
        self.dataContainer = dataContainer
        self.plot_panel = plot_panel
        self.columns = self.dataContainer.longnames.keys()
        sizer = wx.FlexGridSizer(2, 3)
        sizer.Add(wx.StaticText(self, label="Independent variable: "))
        sizer.Add(wx.StaticText(self, label="Dependent variable: "))
        sizer.Add(wx.StaticText(self, label="Color variable: "))
        self.independentCombo = wx.ComboBox(self,
                                            style=wx.CB_READONLY | wx.CB_SORT,
                                            choices=self.columns)
        self.independentCombo.SetStringSelection(self.dataContainer[0].longname)
        sizer.Add(self.independentCombo)
        self.dependentCombo = wx.ComboBox(self,
                                          style=wx.CB_READONLY | wx.CB_SORT,
                                          choices=self.columns)
        self.dependentCombo.SetStringSelection(self.dataContainer[1].longname)
        sizer.Add(self.dependentCombo)
        self.colorCombo = wx.ComboBox(self,
                                      style=wx.CB_READONLY | wx.CB_SORT,
                                      choices=self.columns)
        self.colorCombo.SetStringSelection(self.dataContainer[2].longname)
        sizer.Add(self.colorCombo)
        self.SetSizer(sizer)
        self.Centre()

        self.Bind(wx.EVT_COMBOBOX, self.updatePlot, self.independentCombo)
        self.Bind(wx.EVT_COMBOBOX, self.updatePlot, self.dependentCombo)
        self.Bind(wx.EVT_COMBOBOX, self.updatePlot, self.colorCombo)

    def updatePlot(self, event=None):
        independentVariable = self.independentCombo.GetValue()
        dependentVariable = self.dependentCombo.GetValue()
        colorVariable = self.colorCombo.GetValue()
        if (u''==independentVariable
            or u''==dependentVariable
            or u''==colorVariable):
            return
        self.plot_panel.x_key = independentVariable
        self.plot_panel.y_key = dependentVariable
        self.plot_panel.c_key = colorVariable
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
