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

u"""Provides unittest classes for AutoFocus worker.
"""

__id__ = "$Id$".replace('$','')
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
from pyphant.quantities import Quantity
import numpy
import scipy


def importZStack(filenames, zUnit, zValues):
    from pyphant.core.DataContainer import FieldContainer
    zDim = FieldContainer(data=zValues, unit=zUnit,
                          shortname='z', longname='Z Axis')
    yDim = FieldContainer(data=numpy.arange(.0, 400.0, 1.0) * 1.29,
                          unit=Quantity('1.0 mum'),
                          shortname='y', longname='Y Axis')
    xDim = FieldContainer(data=numpy.arange(.0, 400.0, 1.0) * 1.29,
                          unit=Quantity('1.0 mum'),
                          shortname='x', longname='X Axis')
    imgData = numpy.zeros((zDim.data.shape[0], yDim.data.shape[0],
                           xDim.data.shape[0]), dtype='uint8')
    for i, filename in enumerate(filenames):
        imgData[i] = scipy.misc.imread(os.path.join(importDir, filename),
                                       flatten=True)
    zStack = FieldContainer(data=imgData, dimensions=[zDim, yDim, xDim],
                            shortname='I', longname='ZStack')
    zStack.seal()
    return zStack


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
        zstack = importZStack(
            filenames=filter(lambda x: x.endswith('.tif'),
                             sorted(os.listdir(importDir))),
            zUnit=Quantity('1.0 mum'),
            zValues = numpy.arange(0.0, 601.0, 100.0)
            )
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
        zstack = importZStack(
            filenames=['TestZStack_z03.tif'],
            zUnit=Quantity('1.0 mum'),
            zValues = numpy.array([300.0, ])
            )
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
