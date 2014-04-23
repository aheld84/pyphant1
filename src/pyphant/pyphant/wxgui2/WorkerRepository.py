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

import wx
import cPickle
from pyphant.core.WorkerRegistry import WorkerRegistry


class WorkerRepository(wx.TreeCtrl):
    def __init__(self, *args, **kargs):
        wx.TreeCtrl.__init__(self, *args, **kargs)
        tBIL = WorkerRegistry.getInstance().getToolBoxInfoList()
        rootId = self.AddRoot('toolboxes')
        for tBI in tBIL:
            toolBoxId = self.AppendItem(rootId, tBI.name)
            for workerInfo in tBI.workerInfos:
                wIId = self.AppendItem(toolBoxId, workerInfo.name)
                self.SetItemData(wIId, wx.TreeItemData(workerInfo))
        self.Bind(wx.EVT_TREE_BEGIN_DRAG,
                  self.onDragInit, id=self.GetId())

    def onDragInit(self, event):
        workerInfo = self.GetItemData(event.Item).Data
        if workerInfo is not None:
            dropSource = wx.DropSource(self)
            dump = cPickle.dumps(workerInfo)
            data = wx.CustomDataObject('PYPHANT_WORKER')
            data.SetData(dump)
            dropSource.SetData(data)
            dropSource.DoDragDrop(True)
        event.Skip()
