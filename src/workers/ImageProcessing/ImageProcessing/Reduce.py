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
This module provides the Reduce Worker that extracts a single
image from a stack by reduction of a selectable methode (e.g. 'or')
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer
import ImageProcessing


class BinaryMethod(object):
    import numpy
    mdict = {'or':numpy.bitwise_or,
             'and':numpy.bitwise_and,
             'xor':numpy.bitwise_xor}

    def __init__(self, methodname):
        self.func = self.mdict[methodname]

    def calcStep(self, last, next):
        from copy import deepcopy
        import numpy
        result = deepcopy(last)
        result.data = self.func(last.data.astype(bool), next.data.astype(bool))
        result.seal()
        return result


class iterateImages(object):
    def __init__(self, zstack, subscriber=0):
        self.zstack=zstack
        from pyphant.core.KnowledgeManager import KnowledgeManager
        self.kmanager = KnowledgeManager.getInstance()
        self.subscriber = subscriber
        self.steps = len(self.zstack['emd5'].data)

    def __iter__(self):
        return self.next()

    def next(self):
        for count, emd5 in enumerate(self.zstack['emd5'].data[1:]):
            yield self.kmanager.getDataContainer(emd5)
            self.subscriber %= 99 / self.steps * (count + 2) + 1

    def first(self):
        self.subscriber %= 99 / self.steps + 1
        return self.kmanager.getDataContainer(self.zstack['emd5'].data[0])


class Reduce(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Reduce"
    _sockets = [("zstack", Connectors.TYPE_ARRAY)]
    _params = [('method', 'Method', ['or'], None)]
    _methodPool = {'or' : BinaryMethod('or'),
                   'and' : BinaryMethod('and'),
                   'xor' : BinaryMethod('xor')}
    from pyphant.core.KnowledgeManager import KnowledgeManager
    kmanager = KnowledgeManager.getInstance()

    @Worker.plug(Connectors.TYPE_IMAGE)
    def getReducedImage(self, zstack, subscriber=0):
        method = self._methodPool[self.paramMethod.value]
        iterator = iterateImages(zstack, subscriber)
        last = iterator.first()
        for next in iterator:
            last = method.calcStep(last, next)
        return last
