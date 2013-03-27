#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010, Rectorate of the University of Freiburg
# Copyright (c) 2009-2010, Andreas W. Liehr (liehr@users.sourceforge.net)
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

u"""Provides unittest classes for AutoFocus, LoadZStack
and MarkInclusions worker.
"""

__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
import os
from ImageProcessing import __path__ as ppath
importDir = os.path.join(ppath[0], "tests", "resources",
                         "zstack")


class ZStackTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def check(self, rng, value):
        print rng, value
        assert value >= rng[0] - rng[1] and value <= rng[0] + rng[1], \
               "Value %f not in range (%f, %f)" % (value, rng[0] - rng[1],
                                                   rng[0] + rng[1])

    def testZStack(self):
        print "Importing ZStack..."
        from ImageProcessing.LoadZStack import LoadZStack
        loader = LoadZStack()
        loader.paramPath.value = importDir
        loader.paramDz.value = '100.0 mum'
        loader.paramDy.value = '1.29 mum'
        loader.paramDx.value = '1.29 mum'
        zstack = loader.loadImageAsGreyScale()
        print "Done."
        print "Calculating ZStack-statistics..."
        from ImageProcessing.AutoFocus import AutoFocus
        afw = AutoFocus()
        statistics = afw.getStatistics(zstack)
        print "Done."
        assert len(statistics['diameter'].data) == 2
        imax = statistics['diameter'].data.argmax()
        imin = statistics['diameter'].data.argmin()
        mul = 1.29
        self.check((200.0 * mul, mul), statistics['xPos'].data[imax])
        self.check((200.0 * mul, mul), statistics['yPos'].data[imax])
        self.check((300.0, 0.0), statistics['zPos'].data[imax])
        self.check((20.7 * mul, mul), statistics['diameter'].data[imax])
        self.check((53.0 * mul, mul), statistics['xPos'].data[imin])
        self.check((53.0 * mul, mul), statistics['yPos'].data[imin])
        self.check((300.0, 0.0), statistics['zPos'].data[imin])
        self.check((7.0 * mul, mul), statistics['diameter'].data[imin])

    def testSingle(self):
        print "Importing single image..."
        from ImageProcessing.LoadZStack import LoadZStack
        loader = LoadZStack()
        loader.paramPath.value = os.path.join(importDir, 'TestZStack_z00.tif')
        loader.paramDz.value = '100.0 mum'
        loader.paramDy.value = '1.29 mum'
        loader.paramDx.value = '1.29 mum'
        loader.paramStartz.value = '300.0 mum'
        loader.paramZClip.value = '3:4'
        zstack = loader.loadImageAsGreyScale()
        print "Done."
        print "Calculating single image statistics..."
        from ImageProcessing.AutoFocus import AutoFocus
        afw = AutoFocus()
        statistics = afw.getStatistics(zstack)
        print "Done."
        assert len(statistics['diameter'].data) == 2
        imax = statistics['diameter'].data.argmax()
        imin = statistics['diameter'].data.argmin()
        mul = 1.29
        self.check((200.0 * mul, mul), statistics['xPos'].data[imax])
        self.check((200.0 * mul, mul), statistics['yPos'].data[imax])
        self.check((300.0, 0.0), statistics['zPos'].data[imax])
        self.check((20.7 * mul, 3 * mul), statistics['diameter'].data[imax])
        self.check((53.0 * mul, mul), statistics['xPos'].data[imin])
        self.check((53.0 * mul, mul), statistics['yPos'].data[imin])
        self.check((300.0, 0.0), statistics['zPos'].data[imin])
        self.check((7.0 * mul, mul), statistics['diameter'].data[imin])

    def testMarkInclusions(self):
        from ImageProcessing.LoadZStack import LoadZStack
        from ImageProcessing.MarkInclusions import MarkInclusions
        loader = LoadZStack()
        loader.paramPath.value = importDir
        loader.paramDz.value = '100.0 mum'
        loader.paramDy.value = '1.29 mum'
        loader.paramDx.value = '1.29 mum'
        zstack = loader.loadImageAsGreyScale()
        from ImageProcessing.AutoFocus import AutoFocus
        afw = AutoFocus()
        statistics = afw.getStatistics(zstack)
        minc = MarkInclusions()
        marked = minc.markInclusions(zstack, statistics)
        self.assertEqual(zstack.dimensions, marked.dimensions)
        self.assertEqual(zstack.unit, marked.unit)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
