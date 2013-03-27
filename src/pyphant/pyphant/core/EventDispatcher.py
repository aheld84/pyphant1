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

__version__ = "$Revision$"
# $Source$

class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def registerListener(self, listener, eventType):
        try:
            self._listeners[eventType].append( listener )
        except KeyError:
            self._listeners[eventType] = [listener]

    # The following method is a quick workaround for the shortcoming
    # of this EventDispatcher which offers no control, in which
    # order listeners for the same event are called and the
    # event interface is not specified at all, so there is no
    # functionality like event.skip()
    def registerExclusiveListener(self, listener, eventType):
        self._listeners[eventType] = [listener]

    def unregisterListener(self, listener, eventType=None):
        if eventType:
            self._listeners[eventType].remove( listener )
        else:
            for listeners in self._listeners.values():
                try:
                    listeners.remove(listener)
                except KeyError:
                    pass

    def dispatchEvent(self, event):
        queues = filter(lambda eventType: isinstance(event, eventType),
                        self._listeners.keys())
        for key in queues:
            #if key in self._listeners:
            for listener in self._listeners[key]:
                listener(event)


