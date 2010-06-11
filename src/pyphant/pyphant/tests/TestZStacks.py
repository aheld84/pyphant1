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

u"""Provides unittest classes for ZStack feature.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")


class ZStackTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def check(self, rng, value):
        assert value >= rng[0] - rng[1] and value <= rng[0] + rng[1], \
               "Value %f not in range (%f, %f)" % (value, rng[0] - rng[1],
                                                   rng[0] + rng[1])

    def testZStack(self):
        import os
        from pyphant.core import KnowledgeManager
        from pyphant import __path__ as ppath
        from pyphant.core.ZStackManager import ZStack
        print "Importing ZStack..."
        zstack = ZStack(name="TestCase_ZStack",
                        xml_file=os.path.join(ppath[0], "tests", "resources",
                                              "zstack", "_meta.xml"),
                        temporary=True)
        print "Done."
        print "Calculating ZStack-statistics..."
        from ImageProcessing.AutoFocus import AutoFocus
        afw = AutoFocus()
        statistics = afw.get_statistics_sc(zstack.repr_sc)
        print "Done."
        assert len(statistics['diameter'].data) == 2
        imax = statistics['diameter'].data.argmax()
        imin = statistics['diameter'].data.argmin()
        self.check((200.0, 1.0), statistics['x-pos'].data[imax])
        self.check((200.0, 1.0), statistics['y-pos'].data[imax])
        self.check((300.0, 0.0), statistics['z-pos'].data[imax])
        self.check((20.7, 1.0), statistics['diameter'].data[imax])
        self.check((53.0, 1.0), statistics['x-pos'].data[imin])
        self.check((53.0, 1.0), statistics['y-pos'].data[imin])
        self.check((300.0, 0.0), statistics['z-pos'].data[imin])
        self.check((7.0, 1.0), statistics['diameter'].data[imin])


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
