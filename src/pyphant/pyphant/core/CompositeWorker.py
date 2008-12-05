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

from pyphant.core import EventDispatcher, Worker, Connectors
import copy, pkg_resources

class CompositeWorkerChangedEvent(object):
    def __init__(self, worker, message, data=None):
        self.worker = worker
        self.message = message
        self.data = data

class WorkerAddedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, data=None):
        CompositeWorkerChangedEvent.__init__(self, worker, "Worker Added", data)

class WorkerRemovedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, data=None):
        CompositeWorkerChangedEvent.__init__(self, worker, "Worker Removed", data)

class ConnectionEvent(CompositeWorkerChangedEvent):
    def __init__(self, plug, socket, message, data=None):
        CompositeWorkerChangedEvent.__init__(self, socket.worker, message, data)
        self.plug=plug
        self.socket=socket
class ConnectionCreatedEvent(ConnectionEvent):
    def __init__(self, plug, socket, data=None):
        ConnectionEvent.__init__(self, plug, socket, "Connection created", data)
class ConnectionDestroyedEvent(ConnectionEvent):
    def __init__(self, plug, socket, data=None):
        ConnectionEvent.__init__(self, plug, socket, "Connection destroyed", data)
class ConnectorsExternalizationStateChangedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, connector, data=None):
        CompositeWorkerChangedEvent.__init__(self,worker,"Connectors externalization state changed",data)
        self.connector=connector

class CompositeWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision: $"[11:-1]
    name = "CompositeWorker"
    _params = [("noSockets", "Number of sockets", 0, None),
               ("noPlugs", "Number of plugs", 0, None)]

    def inithook(self):
        self._workers = []
        self._sources = []
        self._sinks = []
        self._eventDispatcher = EventDispatcher.EventDispatcher()
        for i in xrange(self.paramNoSockets.value):
            name = "socket%i" % i
            s = Connectors.ConnectorProxy(self, True, name)
            setattr(self, 'socket'+self.upperFirstLetter(name), s)
            self._sockets[name]=s
        for i in xrange(self.paramNoPlugs.value):
            name = "plug%i" % i
            s = Connectors.ConnectorProxy(self, False, name)
            setattr(self, 'plug'+self.upperFirstLetter(name), s)
            self._plugs[name]=s

    def addWorker(self, worker, data=None):
        self._workers.append(worker)
        if len(worker.getPlugs())==0:
            self._sinks.append(worker)
        if len(worker.getSockets())==0:
            self._sources.append(worker)
        self._notifyListeners(WorkerAddedEvent(worker, data))

    def removeWorker(self, worker, data=None):
        self._workers.remove(worker)
        if worker in self._sources:
            self._sources.remove(worker)
        if worker in self._sinks:
            self._sinks.remove(worker)
        self._notifyListeners(WorkerRemovedEvent(worker, data))

    def getWorkers(self,desiredWorker='',precursor=None):
        if desiredWorker == '':
            result = self._workers
        else:
            result = [w for w in self._workers if w.name == desiredWorker]
            if result == []:
                raise ValueError, "Recipe does not contain Worker %s" % desiredWorker
        if precursor:
            result = [worker for worker in result 
                      if precursor in
                      [socket._plug.worker.name for socket in worker.getSockets()]
                      ]
        return result

    def getSources(self):
        return self._sources

    def getSinks(self):
        return self._sinks

    #pickle
    def __getstate__(self):
        pdict=copy.copy(self.__dict__)
        pdict['_eventDispatcher']=EventDispatcher.EventDispatcher()
        return pdict

    def generateEvents(self, listenerDict):
        map(lambda worker: listenerDict[WorkerAddedEvent](WorkerAddedEvent(worker)), self._workers)
        ##walker=self.createCompositeWorkerWalker()
        def connectionInformer(worker):
            for socket in worker.getSockets():
                if socket.isFull():
                    [(issubclass(ConnectionCreatedEvent, x) and l(ConnectionCreatedEvent(socket.getPlug(), socket))) for (x,l) in listenerDict.items() ]
                    #listenerDict[ConnectionCreatedEvent](ConnectionCreatedEvent(socket.getPlug(), socket))
        connectionInformer(self)
        map(connectionInformer, self._workers)
        ##walker.visit(connectionInformer)

    def createCompositeWorkerWalker(self):
        return CompositeWorkerWalker(self)

    def registerListener(self, listener, eventType=CompositeWorkerChangedEvent):
        self._eventDispatcher.registerListener( listener, eventType)

    def unregisterListener(self, listener, eventType=CompositeWorkerChangedEvent):
        self._eventDispatcher.unregisterListener( listener, eventType )

    def _notifyListeners(self, event):
        self._eventDispatcher.dispatchEvent(event)

    def connectionCreated(self, plug, socket):
        if self.parent:
            self.parent.connectionCreated(plug, socket)
        self._notifyListeners(ConnectionCreatedEvent(plug, socket))

    def connectionDestroyed(self, plug, socket):
        if self.parent:
            self.parent.connectionDestroyed(plug, socket)
        self._notifyListeners(ConnectionDestroyedEvent(plug, socket))

    def workersConnectorStateChanged(self, worker, connector):
        self._notifyListeners(ConnectorsExternalizationStateChangedEvent(worker,connector))


class CompositeWorkerWalker(object):
    def __init__(self, compositeWorker):
        self._compositeWorker=compositeWorker

    def visit(self, visitor):
        visited=[]
        toVisit=copy.copy(self._compositeWorker.getSinks())
        while toVisit:
            worker=toVisit.pop(0)
            visitor(worker)
            visited.append(worker)
            for socket in worker.getSockets():
                plug=socket.getPlug()
                if plug:
                    worker=plug.worker
                    if worker not in visited:
                        toVisit.append(worker)


