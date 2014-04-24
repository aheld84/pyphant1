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

"""
This module provides a visualizer for 3D images

interpreted as a z-stack of 2D images
"""


from pyphant.core.Connectors import TYPE_IMAGE
from pyphant.wxgui2.DataVisReg import DataVisReg
import wx
from pyphant.visualizers.ConfigurablePlot import PlotPanel
import matplotlib
import scipy
import pylab
import os
DEFAULT_CMAP = 'gray'
DEFAULT_CBAD = 'red'


class ZStackPlotPanel(PlotPanel):
    def __init__(self, parent, fieldContainer):
        self.fieldContainer = fieldContainer
        self.cmap = DEFAULT_CMAP
        self.cbad = DEFAULT_CBAD
        PlotPanel.__init__(self, parent)

    def _setfc(self, fieldContainer):
        self._fieldContainer = fieldContainer
        attrs = fieldContainer.attributes

        def scale(quant, name):
            if quant is None:
                return getattr(fieldContainer.data, name[1:])()
            return quant / fieldContainer.unit

        bounds = [scale(attrs.get(name, None), name) \
                  for name in ['vmin', 'vmax']]
        self.vmin, self.vmax = bounds

    def _getfc(self):
        return self._fieldContainer
    fieldContainer = property(_getfc, _setfc)

    def getax(self, figure, img_fc, xlim=None, ylim=None):
        ax = figure.add_subplot(111)
        xdim = img_fc.dimensions[1]
        ydim = img_fc.dimensions[0]
        xmin = scipy.amin(xdim.data)
        xmax = scipy.amax(xdim.data)
        ymin = scipy.amin(ydim.data)
        ymax = scipy.amax(ydim.data)
        image0 = matplotlib.image.NonUniformImage(
            ax, extent=(xmin, xmax, ymin, ymax))
        cmap0 = getattr(pylab.cm, self.cmap)
        image0.set_cmap(cmap0)
        image0.set_norm(matplotlib.colors.Normalize(
            vmin=self.vmin, vmax=self.vmax, clip=False))
        image0.set_data(xdim.data, ydim.data, img_fc.data)
        image = matplotlib.image.NonUniformImage(
            ax, extent=(xmin, xmax, ymin, ymax))
        cmap = getattr(pylab.cm, self.cmap)
        cmap.set_bad(self.cbad, 0.7)
        image.set_cmap(cmap)
        image.set_norm(matplotlib.colors.Normalize(
            vmin=self.vmin, vmax=self.vmax, clip=False))
        image.set_data(xdim.data, ydim.data, img_fc.maskedData)
        ax.images.append(image0)
        ax.images.append(image)
        if xlim is None:
            ax.set_xlim(xmin, xmax)
        else:
            ax.set_xlim(xlim)
        if ylim is None:
            ax.set_ylim(ymin, ymax)
        else:
            ax.set_ylim(ylim)
        ax.set_xlabel(xdim.shortlabel)
        ax.set_ylabel(ydim.shortlabel)
        ax.set_title(img_fc.label)
        from pyphant.visualizers.ConfigurablePlot import F
        self.colorbar = figure.colorbar(
            image, format=F(img_fc), ax=ax)
        return ax

    def draw(self, reset=False):
        self.figure.clear()
        xlim = None
        ylim = None
        if hasattr(self, 'ax') and self.ax.get_xlim() != (0.0, 1.0) and \
               self.ax.get_ylim() != (0.0, 1.0) and not reset:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        self.ax = self.getax(self.figure, self.fieldContainer,
                             xlim=xlim, ylim=ylim)
        self.canvas.draw()

    def saveImage(self, img_fc, path, pixel_resolution):
        dpi = 100
        figsize = (float(pixel_resolution[0] / dpi),
                   float(pixel_resolution[1] / dpi))
        saveFigure = matplotlib.figure.Figure(figsize=figsize, dpi=dpi)
        matplotlib.backends.backend_agg.FigureCanvasBase(
            saveFigure)
        self.getax(saveFigure, img_fc)
        saveFigure.savefig(path, dpi=dpi)


class ZStackConfigPanel(wx.PyPanel):
    def __init__(self, parent, plotPanel):
        wx.PyPanel.__init__(self, parent)
        self.parent = parent
        self.plotPanel = plotPanel
        sizer1 = wx.FlexGridSizer(1, 3)
        self.prevButton = wx.Button(self, label="previous")
        sizer1.Add(self.prevButton)
        self.zChoice = wx.Choice(self, choices=self.parent.zvalues)
        self.zChoice.SetStringSelection(self.parent.zvalues[0])
        sizer1.Add(self.zChoice)
        self.nextButton = wx.Button(self, label="next")
        self.nextButton.SetDefault()
        sizer1.Add(self.nextButton)
        self.saveButton = wx.Button(self, label="save all to -->")
        sizer2 = wx.FlexGridSizer(1, 2)
        sizer2.Add(self.saveButton)
        self.dpc = wx.DirPickerCtrl(self, message="Pick a directory to save "\
                                    "all images")
        sizer2.Add(self.dpc)
        self.cmapChoice = wx.Choice(self, choices=self.parent.cmaps)
        self.cmapChoice.SetStringSelection(DEFAULT_CMAP)
        self.cmapChoice.SetToolTip(wx.ToolTip("select color map"))
        sizer3 = wx.FlexGridSizer(1, 3)
        sizer3.Add(self.cmapChoice)
        self.cbadChoice = wx.Choice(self, choices=self.parent.cbads)
        self.cbadChoice.SetStringSelection(DEFAULT_CBAD)
        self.cbadChoice.SetToolTip(wx.ToolTip("select mask color"))
        sizer3.Add(self.cbadChoice)
        self.resetButton = wx.Button(self, label="reset view")
        sizer3.Add(self.resetButton)
        sizer = wx.FlexGridSizer(3, 1)
        sizer.Add(sizer1)
        sizer.Add(sizer2)
        sizer.Add(sizer3)
        self.SetSizer(sizer)
        self.Centre()
        self.Bind(wx.EVT_BUTTON, self.onNext, self.nextButton)
        self.Bind(wx.EVT_BUTTON, self.onPrev, self.prevButton)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self.onReset, self.resetButton)
        self.Bind(wx.EVT_CHOICE, self.onZChanged, self.zChoice)
        self.Bind(wx.EVT_CHOICE, self.onCChanged, self.cmapChoice)
        self.Bind(wx.EVT_CHOICE, self.onCChanged, self.cbadChoice)
        self.onZChanged()

    def _getZ(self):
        return self.zChoice.GetStringSelection()

    def _setZ(self, zvalue):
        self.zChoice.SetStringSelection(zvalue)
    zvalue = property(_getZ, _setZ)

    def _getZs(self):
        return self.parent.zvalues
    zvalues = property(_getZs)

    def invalidateButtons(self):
        self.prevButton.Enable(self.zid > 0)
        self.nextButton.Enable(self.zid < len(self.zvalues) - 1)

    def onNext(self, Event):
        self.zvalue = self.zvalues[self.zid + 1]
        self.onZChanged()

    def onPrev(self, Event):
        self.zvalue = self.zvalues[self.zid - 1]
        self.onZChanged()

    def onSave(self, Event):
        directory = os.path.realpath(self.dpc.GetPath())
        dial = wx.TextEntryDialog(
            parent=self,
            message="Save all images to '%s'?\nPixel resolution:" % directory,
            caption="Are you sure?",
            defaultValue="800x600")
        retval = dial.ShowModal()
        user_text = dial.GetValue()
        dial.Destroy()
        pixel_resolution = map(int, user_text.split('x'))
        longname = self.parent.dataContainer.longname
        if retval == wx.ID_OK:
            for count, img_fc in enumerate(self.parent.dataContainer):
                path = os.path.join(directory, "%s_%03d.png" \
                                    % (longname, count))
                self.plotPanel.saveImage(img_fc, path, pixel_resolution)
            wx.MessageBox(message="Saved all images to '%s'." % directory,
                          caption='Done!')

    def onReset(self, Event):
        self.plotPanel.draw(reset=True)
        self.GetSizer().Fit(self)

    def onZChanged(self, Event=None):
        self.zid = self.zChoice.GetSelection()
        self.invalidateButtons()
        imgFC = self.parent.dataContainer[self.zid]
        self.plotPanel.fieldContainer = imgFC
        self.plotPanel.draw()
        self.GetSizer().Fit(self)

    def onCChanged(self, Event):
        self.plotPanel.cmap = self.cmapChoice.GetStringSelection()
        self.plotPanel.cbad = self.cbadChoice.GetStringSelection()
        self.plotPanel.draw()
        self.GetSizer().Fit(self)


class ZStackVisualizer(wx.Frame):
    name = 'Z-Stack'

    def __init__(self, dataContainer, show=True):
        self.init_zvalues(dataContainer)
        self.init_cvalues(dataContainer)
        self.dclongname = dataContainer.longname
        wx.Frame.__init__(self, None, -1, "Z-Stack " + dataContainer.longname)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        imgFC = dataContainer[0]
        self.dataContainer = dataContainer
        self.plotPanel = ZStackPlotPanel(self, imgFC)
        self.configPanel = ZStackConfigPanel(self, self.plotPanel)
        self.sizer.Add(self.configPanel, 0, wx.EXPAND)
        self.sizer.Add(self.plotPanel, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Centre()
        self.Show(True)

    def init_zvalues(self, dataContainer):
        zunit = dataContainer.dimensions[0].unit
        self.zvalues = [str(zvalue * zunit) for zvalue \
                        in dataContainer.dimensions[0].data]

    def init_cvalues(self, dataContainer):
        self.cmaps = pylab.cm._cmapnames
        self.cbads = ['red', 'green', 'blue', 'yellow',
                      'black', 'white']
        self.cmaps.sort()
        self.cbads.sort()

    def OnExit(self, event):
        self.Close()


DataVisReg.getInstance().registerVisualizer(TYPE_IMAGE, ZStackVisualizer)
