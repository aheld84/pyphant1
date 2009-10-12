#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009  Rectorate of the University of Freiburg
# Copyright (c) 2009  Andreas W. Liehr
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
pkg_resources.require('pyphant.fmf')

import unittest, numpy
from fmfile import FMFLoader
from pyphant.core.DataContainer import FieldContainer,assertEqual
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity

class FieldContainerCondenseDim(unittest.TestCase):
    def setUp(self):
        self.x = numpy.linspace(0,0.9,10)
        m = numpy.meshgrid(self.x, self.x*5)
        self.valid = numpy.tile(self.x, (10,1))
        self.invalid = [ a.squeeze() for a in numpy.vsplit(m[0]+m[1], len(m[0])) ]

    def testInvalid(self):
        self.assertRaises(AssertionError, FMFLoader.checkAndCondense, self.invalid)

    def testValid(self):
        result = FMFLoader.checkAndCondense(self.valid)
        numpy.testing.assert_array_equal(self.x, result)

class TestColumn2FieldContainer(unittest.TestCase):
    def testStrings(self):
        column = ['Hello','World']
        result = FMFLoader.column2FieldContainer('simple string',column)
        expectedResult = FieldContainer(numpy.array(column),longname='simple string')
        assertEqual(result,expectedResult)

    def testListofStrings(self):
        column = ['World',['Hello', 'World'],'World']
        result = FMFLoader.column2FieldContainer('simple string',column)
        expectedResult = FieldContainer(numpy.array(['World','Hello, World','World']),longname='simple string')
        assertEqual(result,expectedResult)

    def testListofStrings2(self):
        column = [['Hello', 'World'],'World']
        result = FMFLoader.column2FieldContainer('simple string',column)
        expectedResult = FieldContainer(numpy.array(['Hello, World','World']),longname='simple string')
        assertEqual(result,expectedResult)

    def testVariable(self):
        column = [('T',PhysicalQuantity('22.4 degC'),PhysicalQuantity('0.5 degC')),
                  ('T',PhysicalQuantity('11.2 degC'),PhysicalQuantity('0.5 degC'))
                  ]
        result = FMFLoader.column2FieldContainer('temperature',column)
        expectedResult = FieldContainer(numpy.array([22.4,11.2]),error=numpy.array([0.5,0.5]),
                                        mask = numpy.array([False,False]),
                                        unit='1 degC',longname='temperature',shortname='T')
        assertEqual(result,expectedResult)

    def testVariableWithNaN(self):
        column = [('T',PhysicalQuantity('22.4 degC'),PhysicalQuantity('0.5 degC')),
                  ('T',PhysicalQuantity('11.2 degC'),None)
                  ]
        result = FMFLoader.column2FieldContainer('temperature',column)
        expectedResult = FieldContainer(numpy.array([22.4,11.2]),error=numpy.array([0.5,0.0]),
                                        mask = numpy.array([False,False]),
                                        unit='1 degC',longname='temperature',shortname='T')
        assertEqual(result,expectedResult)

    def testVariableFirstNaN(self):
        column = [('T','NaN',PhysicalQuantity('0.5 degC')),
                  ('T',PhysicalQuantity('11.2 degC'),None)
                  ]
        result = FMFLoader.column2FieldContainer('temperature',column)
        expectedResult = FieldContainer(numpy.array([numpy.NaN,11.2]),error=numpy.array([0.5,0.0]),
                                        mask = numpy.array([True,False]),
                                        unit='1 degC',longname='temperature',shortname='T')
        assertEqual(result,expectedResult)

class TestDiscriminatingJouleAndImaginary(unittest.TestCase):
    """In order to discriminate between an imaginary number and unit Joule, imaginary numbers have to be indicated only by a minor capital 'j', while a major capital 'J' indicates the unit Joule.
    """
    def setUp(self):
        self.inputDict = {'complexJ':'1.0j','Joule':'1.0J'}

    def testComplexVale(self):
        """Imaginary numbers are indicated by 'j'."""
        result = FMFLoader.item2value(self.inputDict, 'complexJ')
        self.assertEqual(result,complex(self.inputDict['complexJ']))

    def testJouleValue(self):
        """Physical quantities with unit Joule are indicated by 'J'."""
        result = FMFLoader.item2value(self.inputDict, 'Joule')
        self.assertEqual(result,(PhysicalQuantity(self.inputDict['Joule']),None))
                  
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
