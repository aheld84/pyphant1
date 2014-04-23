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

import threading
import math
import Queue
import wx
import sogl
import pyphant.core.CompositeWorker
import pyphant.core.Connectors as Connectors
import pyphant.core.WorkerRegistry
import pyphant.wxgui2.wxPyphantApplication
import pyphant.wxgui2.DataVisReg
from pyphant.core import Param
import cPickle as pickle


class PyphantDiagram(sogl.Diagram):
    def __init__(
        self, canvas, recipe=pyphant.core.CompositeWorker.CompositeWorker()
        ):
        sogl.Diagram.__init__(self)
        self.SetCanvas(canvas)
        canvas.SetDiagram(self)
        self.workers = {}
        self.connectors = {}
        self.recipe = recipe
        self.createMainConnectors()
        self.recipe.registerListener(
            self.addWorkerShape, pyphant.core.CompositeWorker.WorkerAddedEvent
            )
        self.recipe.registerListener(
            self.onConnectionEvent,
            pyphant.core.CompositeWorker.ConnectionEvent
            )
        self.recipe.registerListener(
            self.onConnectorsExternalizationStateChangedEvent,
            pyphant.core.CompositeWorker.\
                ConnectorsExternalizationStateChangedEvent
            )
        self.recipe.generateEvents(
            {
                pyphant.core.CompositeWorker.WorkerAddedEvent:
                    self.addWorkerShape,
             pyphant.core.CompositeWorker.ConnectionEvent:
                    self.onConnectionEvent,
             pyphant.core.CompositeWorker.\
                    ConnectorsExternalizationStateChangedEvent:
                    self.onConnectorsExternalizationStateChangedEvent
                }
            )
        canvas.Bind(wx.EVT_SIZE, self.onResizeCanvas)

    def createMainConnectors(self):
        sockets = self.recipe.getSockets()
        plugs = self.recipe.getPlugs()
        canvas = self.GetCanvas()
        self.sockets = ConnectorBox(self, sockets, 'Plug')
        self.sockets.Move(
            canvas.getDC(), math.ceil(self.sockets.GetWidth() / 2.0),
            math.ceil(self.sockets.GetHeight() / 2.0), True
            )
        self.plugs = ConnectorBox(self, plugs, 'Socket')

    def onResizeCanvas(self, event):
        canvas = self.GetCanvas()
        size = canvas.GetClientSize()
        self.plugs.Move(
            canvas.getDC(), size.x - math.ceil(self.plugs.GetWidth() / 2.0),
            size.y - math.ceil(self.plugs.GetHeight() / 2.0), True
            )

    def onConnectorsExternalizationStateChangedEvent(self, event):
        if event.worker in self.workers:
            self.workers[event.worker].showConnector(event.connector)

    def onConnectionEvent(self, event):
        try:
            self.connectors[event.socket].updateIncomingPlugs()
        except KeyError:
            pass
        except AttributeError:
            pass

    def addWorkerShape(self, event):
        worker = event.worker
        canvas = self.GetCanvas()
        pos = worker.getAnnotation("pos")
        workerShape = WorkerShape(worker, self)
        workerShape.Move(canvas.getDC(), pos[0], pos[1])
        self.workers[worker] = workerShape
        canvas.Refresh()

    def addWorker(self, pickledWorkerInfo, pos=(0, 0)):
        workerInfo = pickle.loads(str(pickledWorkerInfo))
        workerInfo.createWorker(self.recipe, {"pos": pos})


class ConnectionShape(sogl.LineShape):
    def __init__(self, plug, socket):
        sogl.LineShape.__init__(self)
        self._plug = plug
        self._socket = socket
        canvas = self._socket.GetCanvas()
        self.SetCanvas(canvas)
        self.AddArrow(sogl.ARROW_ARROW)
        self.Show(True)
        canvas.GetDiagram().AddShape(self)
        self.MakeLineControlPoints(2)
        self._plug.AddLine(self, self._socket)

    def destroy(self):
        self._plug.RemoveLine(self)
        canvas = self.GetCanvas()
        canvas.GetDiagram().RemoveShape(self)
        self._socket.connector.pullPlug()
        canvas.Refresh()

    def OnRightClick(self, x, y, keys, attachment):
        self.destroy()


class TypeColors(dict):
    def __init__(self):
        dict.__init__(self)
        self[Connectors.TYPE_ARRAY] = wx.BLUE_BRUSH
        self[Connectors.TYPE_IMAGE] = wx.RED_BRUSH
        self[Connectors.TYPE_INACTIVE] = wx.GREY_BRUSH
        self[Connectors.TYPE_INT] = wx.GREEN_BRUSH
        self[Connectors.TYPE_STRING] = wx.Brush("#FFFF00")
        self[Connectors.TYPE_BOOL] = wx.Brush("#FF00FF")
        self._unknownType = wx.BLACK_BRUSH

    def __getitem__(self, key):
        return self.setdefault(key, self._unknownType)


class ConnectorShape(object):
    TYPE_COLORS = TypeColors()

    def __init__(self, connector):
        self.SetBrush(self.TYPE_COLORS[connector.type])
        self.connector = connector

    def OnBeginDragLeft(self, x, y, keys, attachments):
        pass

    def OnDragLeft(self, draw, x, y, keys, attachments):
        pass

    #necessary to keep ogl from doing stupid stuff
    def OnEndDragLeft(self, x, y, keys, attachments):
        pass


class AcceptPlugs(object):
    def updateIncomingPlugs(self):
        p = self.connector.getPlug()
        if p:
            plugShape = self.GetCanvas().GetDiagram().connectors[p]
            ConnectionShape(plugShape, self)


class SocketShape(ConnectorShape, sogl.RectangleShape, AcceptPlugs):
    def __init__(self, socket):
        sogl.RectangleShape.__init__(self, 10, 10)
        ConnectorShape.__init__(self, socket)


class ParamShape(ConnectorShape, sogl.PolygonShape, AcceptPlugs):
    def __init__(self, param):
        sogl.PolygonShape.__init__(self)
        ConnectorShape.__init__(self, param)
        self._param = param
        r = 5
        self.Create([(r, 0), (0, r), (-r, 0), (0, -r)])

    def updateIncomingPlugs(self):
        super(ParamShape, self).updateIncomingPlugs()
        if self.connector.getPlug():
            self.SetBrush(self.TYPE_COLORS[self.connector.type])
        else:
            self.SetBrush(self.TYPE_COLORS[Connectors.TYPE_INACTIVE])
        self.Draw(self.GetCanvas().getDC())


class ProgressMeter(wx.ProgressDialog):
    def __init__(self, plugName):
        title = u"Calculating %s" % plugName
        message = u"Calculating the result of %s" % plugName
        wx.ProgressDialog.__init__(
            self, title, message, parent=wx.GetApp().getMainFrame()
            )
        self.processes = {}
        self.count = 0
        self.cv = threading.Condition()
        self.percentage = 0
        self.share = 1.0

    def update(self):
        self.cv.acquire()
        self.cv.wait(0.1)
        self.Update(self.percentage)
        self.cv.release()

    def startProcess(self, process):
        self.processes[process] = 0
        self.share = 1.0 / len(self.processes)
        self.updatePercentage()

    def updatePercentage(self):
        self.cv.acquire()
        self.percentage = int(
            sum([x * self.share for x in self.processes.values()])
            )
        self.count += 1
        self.cv.notify()
        self.cv.release()

    def updateProcess(self, process, value):
        self.processes[process] = value
        self.updatePercentage()

    def finishProcess(self, process):
        self.processes[process] = 100
        self.updatePercentage()

    def finishAllProcesses(self):
        self.cv.acquire()
        self.percentage = 100
        self.updatePercentage()
        self.cv.release()


class PlugShape(ConnectorShape, sogl.CircleShape):
    dataVisReg = pyphant.wxgui2.DataVisReg.DataVisReg.getInstance()

    def __init__(self, plug):
        sogl.CircleShape.__init__(self, 10)
        ConnectorShape.__init__(self, plug)
        self._plug = plug

    def _createContextMenu(self):
        self._ids = {}
        self._menu = wx.Menu()
        visMenu = wx.Menu()
        for visualizer in self.dataVisReg.getVisualizers(self._plug.type):
            id = wx.NewId()
            self._ids[id] = visualizer
            visMenu.Append(id, visualizer.name)
            self.GetCanvas().Bind(wx.EVT_MENU, self.visualize, id=id)
        self._menu.AppendMenu(-1, "Visualize", visMenu)

    def visualize(self, event):
        if not self._plug.resultIsAvailable():
            progress = ProgressMeter(self._plug.name)
            exception_queue = Queue.Queue()
            computer = Connectors.Computer(
                self._plug.getResult, exception_queue, subscriber=progress
                )
            computer.start()
            while (progress.percentage < 100) and (computer.isAlive()):
                progress.update()
            progress.finishAllProcesses()
            progress.Destroy()
            if computer.isAlive():
                computer.join()
            result = computer.result
        else:
            result = self._plug._result
        if not result == None:
            self._ids[event.GetId()](result)
        else:
            wx.MessageBox(u"No result is available.\nPlease check the logs.",
                          u"No Result", wx.ICON_ERROR)

    def OnRightClick(self, x, y, keys, attachments):
        if not hasattr(self, '_menu'):
            self._createContextMenu()
        self.GetCanvas().PopupMenu(self._menu)

    def OnEndDragLeft(self, x, y, keys, attachments):
        nearest_object, attachment = self.GetCanvas().FindShape(x, y)
        if isinstance(nearest_object, AcceptPlugs):
            nearest_object.connector.insert(self._plug)
            #nearest_object.updateIncomingPlugs()


class BodyShape(sogl.RectangleShape):
    def __init__(self, workerShape, name):
        sogl.RectangleShape.__init__(self, 100, 50)
        self.workerShape = workerShape
        self.RemoveSensitivityFilter(sogl.OP_DRAG_LEFT | sogl.OP_DRAG_RIGHT)
        self.SetText(name)

    def SetText(self, string):
        """Add a line of text to the shape's default text region."""
        if not self._regions:
            return
        region = self._regions[0]
        region.ClearText()
        new_line = sogl.ShapeTextLine(0, 0, string)
        text = region.GetFormattedText()
        text.append(new_line)
        self._formatted = False

    def OnRightClick(self, x, y, keys, attachment):
        frame = wx.GetTopLevelParent(self.GetCanvas())
        frame._wxPyphantApp.configureWorker(self.workerShape.worker)

    def OnLeftClick(self, x, y, keys, attachment):
        frame = wx.GetTopLevelParent(self.GetCanvas())
        frame._wxPyphantApp.configureWorker(self.workerShape.worker)
        #frame._wxPyphantApp.editCompositeWorker(self.workerShape.worker)


class ConnectorBox(sogl.CompositeShape):
    def __init__(self, diag, connectors, conType):
        sogl.CompositeShape.__init__(self)
        self.diag = diag
        self.SetCanvas(diag.GetCanvas())
        self.connectors = connectors
        self.conShapes = []
        for c in self.connectors:
            if conType == 'Plug':
                cs = PlugShape(c)
            elif conType == 'Socket':
                cs = SocketShape(c)
            else:
                pass
            self.diag.connectors[c] = cs
            self.conShapes.append(cs)
            self.AddChild(cs)
        self.AddConstraint(sogl.Constraint(sogl.CONSTRAINT_ALIGNED_TOP,
                                           self, self.conShapes))
        if len(self.conShapes) > 0:
            self.AddConstraint(sogl.Constraint(sogl.CONSTRAINT_ALIGNED_LEFT,
                                               self, [self.conShapes[0]]))
        for i in xrange(1, len(self.conShapes)):
            self.AddConstraint(sogl.Constraint(sogl.CONSTRAINT_RIGHT_OF,
                                               self.conShapes[i - 1],
                                               [self.conShapes[i]]))
        self.Recompute()
        self.Show(True)


class WorkerShape(sogl.CompositeShape):
    def __init__(self, worker, diag):
        sogl.CompositeShape.__init__(self)
        self.diag = diag
        self.SetCanvas(diag.GetCanvas())
        self.worker = worker
        bodyShape = BodyShape(self, worker.getParam('name').value)
        self.AddChild(bodyShape)

        self.socketShapes = []
        for socket in worker.getSockets():
            socketShape = SocketShape(socket)
            self.diag.connectors[socket] = socketShape
            self.AddChild(socketShape)
            self.socketShapes.append(socketShape)

        self.plugShapes = []
        for plug in worker.getPlugs():
            plugShape = PlugShape(plug)
            self.diag.connectors[plug] = plugShape
            self.AddChild(plugShape)
            self.plugShapes.append(plugShape)

        self.paramShapes = []
        for param in worker.getParamList():
            paramShape = ParamShape(param)
            self.diag.connectors[param] = paramShape
            self.AddChild(paramShape)
            self.paramShapes.append(paramShape)

        if self.socketShapes != []:
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_TOP, bodyShape,
                    self.socketShapes
                    )
                )
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_LEFT, bodyShape,
                    [self.socketShapes[0]]
                    )
                )
            for i in xrange(1, len(self.socketShapes)):
                self.AddConstraint(
                    sogl.Constraint(
                        sogl.CONSTRAINT_RIGHT_OF, self.socketShapes[i - 1],
                        [self.socketShapes[i]]
                        )
                    )

        if self.plugShapes != []:
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_BOTTOM, bodyShape,
                    self.plugShapes
                    )
                )
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_RIGHT, bodyShape,
                    [self.plugShapes[0]]
                    )
                )
            for i in xrange(1, len(self.plugShapes)):
                self.AddConstraint(
                    sogl.Constraint(
                        sogl.CONSTRAINT_LEFT_OF, self.plugShapes[i - 1],
                        [self.plugShapes[i]]
                        )
                    )

        if self.paramShapes != []:
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_TOP, bodyShape,
                    self.paramShapes
                    )
                )
            self.AddConstraint(
                sogl.Constraint(
                    sogl.CONSTRAINT_ALIGNED_RIGHT, bodyShape,
                    [self.paramShapes[0]]
                    )
                )
            for i in xrange(1, len(self.paramShapes)):
                self.AddConstraint(
                    sogl.Constraint(
                        sogl.CONSTRAINT_LEFT_OF, self.paramShapes[i - 1],
                        [self.paramShapes[i]]
                        )
                    )
        self.Recompute()

        self.RemoveSensitivityFilter(sogl.OP_CLICK_LEFT, False)
        #self.AddSensitivityFilter(sogl.OP_CLICK_LEFT, True)

        self.worker.registerParamListener(
            lambda event: (
                bodyShape.SetText(event.newValue),
                bodyShape.GetCanvas().Refresh()
                ),
            'name',
            Param.ParamChanged
            )
        self.Show(True)

        map(
            lambda con: self.diag.connectors[con].Show(False),
            filter(
                lambda connector: not connector.isExternal,
                self.diag.connectors
                )
            )

    def hideConnector(self, connector):
        try:
            self.diag.connectors[connector].Show(False)
        except KeyError:
            pass

    def showConnector(self, connector):
        try:
            self.diag.connectors[connector].Show(True)
        except KeyError:
            pass

    def OnMovePost(self, dc, x, y, old_x, old_y, display=True):
        self.worker._annotations["pos"] = (x, y)
