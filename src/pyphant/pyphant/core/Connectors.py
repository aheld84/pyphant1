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

import copy, threading, inspect, logging
import Queue

class FullSocketError(ValueError):
    pass

TYPE_ARRAY = 'scipy.array'
TYPE_IMAGE = 'pil.image'
TYPE_INT = type(2)
TYPE_STRING = type("")
SUBTYPE_FILE = "filename"
SUBTYPE_INSTANT = "instant"
TYPE_INACTIVE = type(None)
TYPE_BOOL = type(True)
DEFAULT_DATA_TYPE = TYPE_ARRAY

class Connector(object):
    def __init__(self, worker, name, type=DEFAULT_DATA_TYPE, pre=""):
        self.worker = worker
        self.name = name
        self.type = type
        self._isExternal = True
        self.pre = pre

    def _getIsExternal(self):
        return self._isExternal

    def _setIsExternal(self, isExternal):
        if isExternal != self._isExternal:
            self._isExternal = isExternal
            self.worker.connectorsExternalizationStateChanged(self)
    isExternal = property(_getIsExternal, _setIsExternal)
    id = property(lambda self:
                  self.worker.id+"."+self.pre+self.name.capitalize())

class Computer(threading.Thread):
    def __init__(self, method, exception_queue, **kwargs):
        threading.Thread.__init__(self)
        self.method = method
        self.kwargs = kwargs
        self.result = None
        self.exception_queue = exception_queue

    def run(self):
        if self.method:
            try:
                self.result = self.method(subscriber=self.kwargs["subscriber"])
            except Exception, e:
                logging.getLogger('pyphant').debug(
                    u"An unhandled exception occured in the calculation.",
                    exc_info = True)
                self.exception_queue.put(e)
                raise


class Plug(Connector):
    def __init__(self, worker, name, type=DEFAULT_DATA_TYPE):
        Connector.__init__(self, worker, name, type, "plug")
        self._result = None
        self._resultLock = threading.Lock()
        self._sockets = []

    def __getstate__(self):#this could be done with marshalling
        pdict = copy.copy(self.__dict__)
        pdict['_result'] = None
        del pdict['_resultLock']
        return pdict

    def __setstate__(self, pdict):
        self.__dict__.update(pdict)
        self._resultLock = threading.Lock()

    def addSocket(self, socket):
        self._sockets.append(socket)

    def removeSocket(self, socket):
        self._sockets.remove(socket)

    def invalidate(self, event=None):
        self._resultLock.acquire()
        self._result = None
        for socket in self._sockets:
            socket.invalidate()
        self._resultLock.release()

    def resultIsAvailable(self):
        """Indicates whether a precalculated result is available.

        This is not threadsafe, i.e. by the time this function returns
        a formerly available result may have been invalidated, or a
        calculation may have finished. Use as an indicator only."""
        return (self._result != None)


class Updater(object):
    def __init__(self, subscriber, process):
        self.subscriber = subscriber
        self.process = process

    def __imod__(self, percentage):
        if self.subscriber:
            self.subscriber.updateProcess(self.process, percentage)
        return self

class CalculatingPlug(Plug):
    def __init__(self, method, name, type=DEFAULT_DATA_TYPE):
        Plug.__init__(self, method.im_self, name, type)
        self._methodName = method.func_name
        self._func = self.createWrapper(method)

    def createWrapper(self, method):
        args, varargs, varkw, defaults = inspect.getargspec(method)
        sockets = args[1:-1]
        name = method.func_name+'PyphantWrapper'
        l = 'def '+name+'(subscriber, method=method, process=self):\n'
        l += '\texception_queue=Queue.Queue()\n'
        for s in sockets:
            l += '\t'+s+'=Computer(method.im_self.getSocket("'
            l += s+'").getResult, exception_queue, subscriber=subscriber)\n'
        for s in sockets:
            l += '\t'+s+'.start()\n'
        for s in sockets:
            l += '\t'+s+'.join()\n'
        l += '\texceptions=[]\n'
        l += '\twhile not exception_queue.empty():\n'
        l += '\t\texceptions.append(exception_queue.get())\n'
        l += '\t\texception_queue.task_done()\n'
        l += '\tif len(exceptions)>0:\n'
        l += '\t\traise RuntimeError, str(exceptions)\n'
        #If no sockets are needed the comma in the next line will be erased,
        #so do not add a space!
        l += '\treturn method( subscriber=Updater(subscriber, process),'
        for s in sockets:
            l += s+'='+s+'.result,'
        l = l[:-1]+')\n'
        exec l
        return eval(name)

    def __getstate__(self):#this could be done with marshalling
        pdict = super(CalculatingPlug, self).__getstate__()
        del pdict['_func']
        return pdict

    def __setstate__(self, pdict):
        super(CalculatingPlug, self).__setstate__(pdict)
        self._func = self.createWrapper(getattr(self.worker, self._methodName))

    def getResult(self, subscriber = None):
        self._resultLock.acquire()
        try:
            if not self.resultIsAvailable():
                if subscriber:
                    subscriber.startProcess(self)
                self._result = self._func(subscriber)
                if subscriber:
                    subscriber.finishProcess(self)
            result = self._result
        finally:
            self._resultLock.release()
        return result

class Socket(Connector):
    def __init__(self, worker, name, type=DEFAULT_DATA_TYPE):
        Connector.__init__(self, worker, name, type, "socket")
        self._plug = None

    def isFull(self):
        return self._plug != None

    def insert(self, plug):
        assert(isinstance(plug, Plug))
        if self.isFull():
            raise FullSocketError()
        self._plug = plug
        plug.addSocket(self)
        self.invalidate()
        try:
            self.worker.connectionCreated(plug, self)
        except AttributeError:
            ## WARNING: Next line is a hack! Check for parentship properly!
            if self.worker.parent:
                self.worker.parent.connectionCreated(plug, self)

    def pullPlug(self):
        self._plug.removeSocket(self)
        plug = self._plug
        self._plug = None
        self.invalidate()
        try:
            self.worker.connectionDestroyed(plug, self)
        except AttributeError:
            ## WARNING: Next line is a hack! Check for parentship properly!
            if self.worker.parent:
                self.worker.parent.connectionDestroyed(plug, self)

    def invalidate(self, event=None):
        self.worker.invalidate(self)

    def getPlug(self):
        return self._plug

    def getResult(self, subscriber = None):
        return self._plug.getResult(subscriber)
    value = property(getResult)

class ConnectorProxy(Socket, Plug):
    def __init__(self, worker, isSocket, name, type=DEFAULT_DATA_TYPE):
        Plug.__init__(self, worker, name, type)
        Socket.__init__(self, worker, name, type)
        self._result = None
        self.isSocket = isSocket
        self._resultLock = threading.Lock()
        self._sockets = []

    def __getstate__(self):#this could be done with marshalling
        pdict = copy.copy(self.__dict__)
        pdict['_result'] = None
        del pdict['_resultLock']
        return pdict

    def __setstate__(self, pdict):
        self.__dict__.update(pdict)
        self._resultLock = threading.Lock()

    def invalidate(self, event=None):
        #if self.isSocket:
        #    Socket.invalidate(self, event)
        #else:
        Plug.invalidate(self, event)

    def getResult(self, subscriber=None):
        return self._plug.getResult(subscriber)
    value = property(getResult)
