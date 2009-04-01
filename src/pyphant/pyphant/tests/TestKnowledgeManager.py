#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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

u"""Provides unittest classes 
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")

from pyphant.core.KnowledgeManager import KnowledgeManager
import pyphant.core.PyTablesPersister as ptp
from pyphant.core.FieldContainer import FieldContainer
import numpy as N
import tables
import tempfile
import os

import logging


class KnowledgeManagerTestCase(unittest.TestCase):
    def setUp(self):
        a = N.array([0, 1, 2, 3])
        self._fc = FieldContainer(a)
        self._fc.seal()

    def testGetLocalFile(self):
        
        h5fileid, h5name = tempfile.mkstemp(suffix='.h5',prefix='test-')
        os.close(h5fileid)

        h5 = tables.openFile(h5name,'w')
        resultsGroup = h5.createGroup("/", "results")
        ptp.saveResult(self._fc, h5)
        h5.close()

        km = KnowledgeManager.getInstance()

        km.registerURL('file://'+h5name)

        km_fc = km.getDataContainer(self._fc.id)

        self.assertEqual(self._fc, km_fc)

        os.remove(h5name)

if __name__ == "__main__":
    import sys

    logger = logging.getLogger('pyphant')
    

    hdlr = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('[%(name)s|%(levelname)s] %(message)s')
    hdlr.setFormatter(formatter)

    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
