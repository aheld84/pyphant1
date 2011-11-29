#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2009, Rectorate of the University of Freiburg
# Copyright (c) 2009-2011, Andreas W. Liehr (liehr@users.sourceforge.net)
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

# $Source$

import pkg_resources
pkg_resources.require('pyphant')
import unittest
from pyphant.quantities.ParseQuantities import parseDateTime,str2unit
from pyphant.quantities import Quantity


class TestParseDateTime(unittest.TestCase):
    """
    >>>parseDateTime('2004-08-21 12:00:00+-12hr')
    (Quantity(731814.5, 'd'), Quantity(0.5, 'd'))
    >>>parseDateTime('2004-08-21 12:00:00')
    (Quantity(731814.5, 'd'), None)
    """

    def testWithError(self):
        self.assertEqual(parseDateTime('2004-08-21 12:00:00+-12hr'),
                         (Quantity(731814.5, 'd'), Quantity(0.5, 'd'))
                         )

    def testWithErrorOldDeprecatedAbbreviation(self):
        self.assertEqual(parseDateTime('2004-08-21 12:00:00+-12h'),
                         (Quantity(731814.5, 'd'), Quantity(0.5, 'd'))
                         )


class TestStr2unit(unittest.TestCase):
    """Test the correct conversion of strings to quantities or floats."""

    def setUp(self):
        self.inputDict = {'complexJ':'1.0j', 'Joule':'1.0J'}

    def testSimpleQuantity(self):
        """
        The the conversion of a simple textual quantity specification
        to a quantity object.
        """
        expected = Quantity('1V')
        result = str2unit('1V')
        self.assertEqual(expected, result)

    def testComplexNumber(self):
        """
        Complex numbers have to be denoted by small 'j',
        in oder to discriminate them from Joule.
        """
        result = str2unit(self.inputDict['complexJ'])
        self.assertEqual(result, complex(self.inputDict['complexJ']))

    def testJouleValue(self):
        """Physical quantities with unit Joule are indicated by 'J'."""
        result = str2unit(self.inputDict['Joule'])
        self.assertEqual(result, Quantity(self.inputDict['Joule']))

    def testHourPlanck(self):
        """
        In FMF 1.0 unit 'h' denotes hours,
        while in FMF 1.1 'h' denotes the Planck constant.
        """
        result = str2unit('1h')
        self.assertEqual(result, Quantity('6.62606896e-34 J*s'))
        result = str2unit('1h', FMFversion='1.0')
        self.assertEqual(result, Quantity('3600s'))

    def testFloatAccuracy(self):
        result = str2unit('16.8 mm', FMFversion='1.0')
        diff = result - Quantity('16.8 mm')
        self.assertEqual(abs(diff.value) < 2e-14,True)
        result = str2unit('16.8 mm', FMFversion='1.0')
        diff = Quantity('16.8 mm')
        self.assertEqual(result, diff)

    def testGravitationalConstant(self):
        result = str2unit("1 Grav", FMFversion="1.0")
        self.assertEqual(result, str2unit('6.67259e-11 m**3/kg/s**2'))


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
