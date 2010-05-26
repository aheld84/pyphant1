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

import Queue
import wx
from pyphant.core.Connectors import Computer

        

class ConfigureFrame(wx.Dialog):
    def __init__(self, parent, paramVisReg, worker):
        from PyphantDiagram import ProgressMeter
        self._paramVisReg=paramVisReg
        wx.Dialog.__init__(self, parent, -1, "Configure "+worker.getParam("name").value)
        self._paramDict={}
        progress = ProgressMeter("Acquiring Param data")
        exception_queue = Queue.Queue()
        computer = Computer(worker.refreshParams, exception_queue, subscriber=progress)
        computer.start()
        while (progress.percentage<100) and (computer.isAlive()):
            progress.update()
        progress.finishAllProcesses()
        progress.Destroy()
        if computer.isAlive():
            computer.join()
        pl = worker.getParamList()
        if len(pl) <= 0:
            self.Add(wx.StaticText(self, label="Nothing to be configured"))
        else:
            sizer = wx.FlexGridSizer(len(pl),3,5,5)
            sizer.Add(wx.StaticText(self, label="Label"))
            sizer.Add(wx.StaticText(self, label="Value"))
            sizer.Add(wx.StaticText(self, label="is external"))
            for param in pl:
                sizer.Add(wx.StaticText(self, label=param.displayName))
                vis=self._paramVisReg.createVisualizerFor(self, param)
                sizer.Add(vis)
                checkBox=wx.CheckBox(self)
                checkBox.SetValue(param.isExternal)
                sizer.Add(checkBox)
                self._paramDict[vis]=(param,checkBox)
            sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL))
            self.SetSizer(sizer)
            sizer.Fit(self)

    def applyAll(self, event=None):
        for (vis,(param,checkBox)) in self._paramDict.items():
            try:
                param.value=vis.getValue()
                param.isExternal=checkBox.GetValue()
            except ValueError, (e):
                print "Caught a ValueError in ", vis, ":", e

