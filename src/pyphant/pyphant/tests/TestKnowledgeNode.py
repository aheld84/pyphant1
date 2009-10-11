#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""Provides unittest classes for KnowledgeNode.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
from pyphant.core.KnowledgeNode import (KnowledgeNode, RemoteKN)


class KnowledgeNodeTestCase(unittest.TestCase):
    def setUp(self):
        self.kn = KnowledgeNode(start=True)

    def tearDown(self):
        self.kn.stop()

    def testUUID(self):
        from urllib2 import urlopen
        stream = urlopen(self.kn.url + 'uuid/')
        uuid = stream.readline()
        stream.close()
        assert uuid == self.kn.km.uuid
        assert uuid == self.kn.uuid

    def testManageRemotes(self):
        self.kn.register_remote('127.0.0.1', -1)
        dummy = RemoteKN('127.0.0.1', -1, status=2)
        assert dummy in self.kn.remotes
        self.kn.remove_remote('127.0.0.1', -1)
        assert not dummy in self.kn.remotes

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
