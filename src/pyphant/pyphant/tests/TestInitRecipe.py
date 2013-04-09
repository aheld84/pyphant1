# -*- coding: utf-8 -*-

# Copyright (c) 2013, Rectorate of the University of Freiburg
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

import unittest
from pyphant.core import (Worker, Connectors, CompositeWorker)
from pyphant.core.H5FileHandler import H5FileHandler
import pkg_resources
import tempfile
import shutil
import os
import logging


class DummyProvider(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant").version
    name = "DummyProvider"
    _params = [("source", u"Source", "", None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def load(self, subscriber=0):
        if not self.paramSource.value:
            raise ValueError('Not initialized!')
        else:
            return [42, -1]

    def __hash__(self):
        return 2


class DummyConsumer(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant").version
    name = "DummyConsumer"
    _params = [("foo", u"Foo", [0], None)]
    _sockets = [("socket1", Connectors.TYPE_IMAGE)]

    def refreshParams(self, subscriber=None):
        if self.socketSocket1.isFull():
            values = self.socketSocket1.getResult(subscriber)
            self.paramFoo.possibleValues = values

    @Worker.plug(Connectors.TYPE_IMAGE)
    def check(self, socket1, subscriber=0):
        return True

    def __hash__(self):
        return 1


class RaiseHandler(logging.Handler):
    def handle(self, record):
        if record.exc_info:
            raise record.exc_info[1]


class TestInitalizationOrder(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.join(self.tmpdir, 'init_order.h5')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def testInitializationOrder(self):
        logger = logging.getLogger("pyphant")
        loghandler = RaiseHandler()
        logger.addHandler(loghandler)
        recipe = CompositeWorker.CompositeWorker()
        recipe.addWorker(DummyConsumer())
        recipe.addWorker(DummyProvider())
        recipe.getWorker('DummyProvider').paramSource.value = 'The Universe'
        plug = recipe.getWorker('DummyProvider').getPlug('load')
        socket = recipe.getWorker('DummyConsumer').getSocket('socket1')
        socket.insert(plug)
        handler = H5FileHandler(self.filename, 'w')
        with handler:
            handler.saveRecipe(recipe)
        handler = H5FileHandler(self.filename, 'r')
        with handler:
            handler.loadRecipe()


if __name__ == '__main__':
    unittest.main()
