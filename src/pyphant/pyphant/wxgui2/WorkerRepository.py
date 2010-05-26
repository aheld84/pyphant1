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

import wx
import cPickle
import pyphant.core.WorkerRegistry

class WorkerRepository(wx.ScrolledWindow):
    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0):
        wx.ScrolledWindow.__init__(self, parent, id)
        workerRegistry = pyphant.core.WorkerRegistry.WorkerRegistry
        self._workerRegistry = workerRegistry.getInstance()
        self._boxSizer = wx.BoxSizer(wx.VERTICAL)
        self.initFoldPanelBar()
        self.SetSizer(self._boxSizer)
        self.SetScrollRate(1, 1)
        self._boxSizer.SetVirtualSizeHints(self)

    def initFoldPanelBar(self):
        map(self.addWorkerButton, self._workerRegistry.getWorkers())

    def addWorkerButton(self, workerInfo):
        btn = WorkerButton(self, workerInfo)
        self._boxSizer.Add(btn, 1, wx.EXPAND, wx.ALL, 10)


class WorkerButton(wx.Button):
    def __init__(self, parent, workerInfo):
        name = workerInfo.name
        wx.Button.__init__(self, parent, label=name)
        self._workerInfo = workerInfo
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)

    def onLeftDown(self, evt):
        dropSource = wx.DropSource(self)
        pickledObj = cPickle.dumps(self._workerInfo)
        data = wx.TextDataObject(pickledObj)
        dropSource.SetData(data)
        dragResult = dropSource.DoDragDrop(True)
