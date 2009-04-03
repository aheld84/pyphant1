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
The Worker module provides the Worker base class and some support.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import types, logging
from pyphant.core import Connectors, Param, WorkerRegistry

class WorkerInfo(object):
##    __slots__ = ["name", "createWorker"] #not possible due to pickling restrictions.
    def __init__(self, name, createWorker):
        self.name=name
        self.createWorker=createWorker

def plug(returnType):
    def setPlug(_plug):
        setattr(_plug, 'isPlug', True)
        setattr(_plug, 'returnType', returnType)
        return _plug
    return setPlug


def identifyPlugs(n,cdict):
    f=cdict[n]
    return isinstance(f, types.FunctionType)\
           and getattr(f, 'isPlug', False)

class WorkerFactory(type):
    workerRegistry = WorkerRegistry.WorkerRegistry.getInstance()
    log = logging.getLogger("pyphant")
    def __init__(cls, name, bases, cdict):
        cls._plugs=[]
        for f in filter(lambda key : identifyPlugs(key, cdict), cdict):
            cls._plugs.append((f, cdict[f]))
        super(WorkerFactory, cls).__init__(name, bases, cdict)
        if cls.__name__ != 'Worker':
            WorkerFactory.workerRegistry.registerWorker(WorkerInfo(cls.name,cls))

class Worker(object):
    API = 2
    REVISION = "$Revision$"[11:-1]

    __metaclass__ = WorkerFactory
    _sockets=[]
    _plugs=[]
    _params=[]
    DEFAULT_ANNOTATIONS={"pos":(0,0)}
    def __init__(self, parent=None, annotations={}):
        self._annotations=annotations
        map(lambda k: self._annotations.setdefault(k, Worker.DEFAULT_ANNOTATIONS[k]),
            Worker.DEFAULT_ANNOTATIONS.keys())
        self.parent=parent
        self.initSockets(self._sockets)
        self.initPlugs(self._plugs)
        self.initParams(self._params)
        self.inithook()
        if parent:
            basename=self.getParam('name').value
            for i in xrange(10000):
                try:
                    parent.addWorker(self)
                    break
                except ValueError:
                    self.getParam('name').value = basename+'_%i'%i

    def _id(self):
        if self.parent != None:
            pre = self.parent.id
        else:
            pre = ""
        if pre != "":
            return pre+"."+self.getParam('name').value
        else:
            return self.getParam('name').value
    id = property(_id)

    def inithook(self):
        pass

    def refreshParams(self, subscriber=None):
        pass

    def initPlugs(self, plugs):
        self._plugs={}
        for (name, func) in plugs:
            p = Connectors.CalculatingPlug(getattr(self, func.func_name), name, func.returnType)
            setattr(self, 'plug'+self.upperFirstLetter(name), p)
            self._plugs[name]=p

    def initSockets(self, sockets):
        self._sockets={}
        for socket in sockets:
            if isinstance(socket, tuple):
                name=socket[0]
                type=socket[1]
            else:
                name=socket
                type=Connectors.DEFAULT_DATA_TYPE
            s=Connectors.Socket(self, name, type)
            setattr(self, 'socket'+self.upperFirstLetter(name), s)
            self._sockets[name]=s

    def upperFirstLetter(self, name):
        return name[0].upper()+name[1:]

    def initParams(self, params):
        self._params={}
        self._order=[]
        self.addParam('name',Param.ParamFactory.createParam(self,'name','Name',
                                                            self.__class__.__name__))
        for (name, displayName, value, subtype) in params:
            p=Param.ParamFactory.createParam(self, name, displayName, value, subtype)
            setattr(self, 'param'+self.upperFirstLetter(name), p)
            self.addParam(name, p)

    def setAnnotation(self, key, value):
        self._annotations[key]=value

    def getAnnotation(self, key):
        try:
            return self._annotations[key]
        except KeyError:
            return None

    def getAnnotations(self):
        return self._annotations

    def addParam(self, name, param):
        if name in self._params:
            raise AttributeError, "Parameter \"" + name + "\" already exists."
        self._params[name]=param
        self._order.append(name)

    def getParam(self, name):
        return self._params[name]

    def getParamList(self):
        paramList=[]
        for name in self._order:
            paramList.append(self._params[name])
        return paramList

    def registerParamListener(self, listener, param, eventType):
        self.getParam(param).registerListener(listener, eventType)

    def unregisterParamListener(self, vetoer, param, eventType):
        self.getParam(param).unregisterListener(listener, eventType)

    def invalidate(self, event=None):
        map(lambda p: p.invalidate(), self._plugs.values())

    def getSocket(self, name):
        return self._sockets[name]

    def getSockets(self):
        return self._sockets.values()

    def getPlug(self, name):
        return self._plugs[name]

    def getPlugs(self):
        return self._plugs.values()

    def connectorsExternalizationStateChanged(self, connector):
        if self.parent:
            self.parent.workersConnectorStateChanged(self,connector)
