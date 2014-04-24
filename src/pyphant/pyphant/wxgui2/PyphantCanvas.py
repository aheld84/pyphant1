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

"""This module provides a GUI element for arranging the workers in a recipe"""

import wx
import sogl
from pyphant.wxgui2 import PyphantDiagram
import pyphant.core.CompositeWorker as CompositeWorker


class PyphantCanvas(sogl.ShapeCanvas):
    def __init__(
        self, parent, recipe=CompositeWorker.CompositeWorker(),
        id=-1, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=wx.NO_BORDER, name="PyphantCanvas"
        ):
        sogl.ShapeCanvas.__init__(self, parent, id, pos, size, style, name)
        #self.SetVirtualSize((1100,1000))
        self.SetScrollRate(20, 20)
        self.dropTarget = CanvasDropTarget(self)
        self.SetDropTarget(self.dropTarget)
        self.diagram = PyphantDiagram.PyphantDiagram(self, recipe)

    def getDC(self):
        return wx.ClientDC(self)

#    def OnBeginDragLeft(self, x, y, keys=0):
#        print "A"
#        print self._draggedShape


class CanvasDropTarget(wx.PyDropTarget):
    def __init__(self, parent):
        wx.PyDropTarget.__init__(self)
        self.parent = parent
        self.df = wx.CustomDataFormat('PYPHANT_WORKER')
        self.data = wx.CustomDataObject(self.df)
        self.SetDataObject(self.data)

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, d):
        if self.GetData():
            dump = self.data.GetData()
            self.parent.diagram.addWorker(dump, (x, y))
        #self.parent.Refresh()
        return d
