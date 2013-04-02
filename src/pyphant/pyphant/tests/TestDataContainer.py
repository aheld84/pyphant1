#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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

u"""Provides unittest classes FieldContainerTestCase, SampleContainerTest.
"""


import unittest
import pkg_resources
pkg_resources.require("pyphant")

import scipy
import copy
from pyphant.quantities import Quantity
from pyphant.core.DataContainer import (INDEX,
                                        generateIndex,
                                        FieldContainer,
                                        SampleContainer,
                                        DataContainer,
                                        assertEqual)
import numpy.testing as nt
import numpy

class DataContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DataContainer('variable', 'v')
        self.dc0 = DataContainer('variable', 'v_0')

    def testNoSubscriptPersistent(self):
        result = self.dc.appendSubscript('i')
        self.assertEqual(result, 'v_{i}')
        self.assertEqual(self.dc.shortname, 'v_{i}')

    def testSubscriptPersistent(self):
        result = self.dc0.appendSubscript('i')
        self.assertEqual(result, 'v_{0,i}')
        self.assertEqual(self.dc0.shortname, 'v_{0,i}')

    def testNoSubscriptNotPersistent(self):
        result = self.dc.appendSubscript('i', persistent=False)
        self.assertEqual(result, 'v_{i}')
        self.assertEqual(self.dc.shortname, 'v')

    def testSubscriptNotPersistent(self):
        result = self.dc0.appendSubscript('i', persistent=False)
        self.assertEqual(result, 'v_{0,i}')
        self.assertEqual(self.dc0.shortname, 'v_0')

    def testDefaultAttribute(self):
        """
        Checking if the default attribute has correctly been set to an empty
        dictionary.
        """
        self.assertEqual(self.dc.attributes,
                         {},
                         'Expected an empty dictionary as attribute, \
but found %s.' % self.dc.attributes )

class FieldContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.testData = scipy.array([[0., 1., 2.], [3., 4., 5.], [6., 7., 8.]])
        self.testMask = self.testData > 5
        self.longname = u"Sampled Data"
        self.shortname = u"I\\omega"
        self.unit = Quantity('3.14 m')

    def testGenerateIndex(self):
        i=0
        n=1000
        index = generateIndex(i,n)
        self.assertEqual(index.dimensions, INDEX)
        self.assertEqual(index.longname, 'Index')
        self.assertEqual(index.shortname, 'i')
        self.assertEqual(index.unit, 1)
        self.assertFalse(index.error)
        self.assertTrue(scipy.alltrue(index.data == scipy.arange(0,n)))

    def testLabeling(self):
        field = FieldContainer(self.testData,
                               1,
                               longname=self.longname,
                               shortname=self.shortname)
        self.assertEqual(field.label,"%s $%s(i,j)$ / a.u." % (self.longname,
                                                              self.shortname))
        field = FieldContainer(self.testData,
                               self.unit,
                               longname=self.longname,
                               shortname=self.shortname)
        self.assertEqual(field.label,"%s $%s(i,j)$ / %s" % (self.longname,
                                                            self.shortname,
                                                            self.unit))

    def testSeal(self):
        field = FieldContainer(self.testData,
                               1,
                               longname=self.longname,
                               shortname=self.shortname)
        field.seal()
        self.assertNotEqual(field.id, None)
        self.assertNotEqual(field.hash, None)
        try:
            field.data = scipy.array([1, 2, 3])
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not \
                        prohibited.")
        try:
            field.data[1] = 4
        except RuntimeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not \
                        prohibited.")
        try:
            field.dimensions[0] = copy.deepcopy(field)
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer's dimension \
                        was not prohibited.")

#This test is broken since it produces an invalid FieldContainer.
#I am not sure how to fix it or what its intent is.
#FIXME:
#    def testSealedFieldContainerWithDirectDimensionsModification(self):
#        field = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
#        field.dimensions=[copy.deepcopy(field)]
#        try:
#            field.seal()
#        except AttributeError, e:
#            self.fail("Direct setting of attribute .dimensions has not instantiated a dimensionList object: %s"%e)

    def testDeepcopy(self):
        field = FieldContainer(self.testData,
                               1,
                               longname=self.longname,
                               shortname=self.shortname)
        copiedField=copy.deepcopy(field)
        self.assertEqual(field, copiedField)
        field.seal()
        copiedField.seal()
        self.assertEqual(field, copiedField)
        #equal because only real data is considered:
        self.assertEqual(field.hash, copiedField.hash)
        #unique due to timestamp in dimension ids:
        self.assertNotEqual(field.id, copiedField.id)

    def testEqual(self):
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname + "bu",
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname + 'a')
        self.assertEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                "1 km",
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1000 m",
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        #necessary to test the != operator (__ne__):
        assert(not (field1 != field2))
        field1 = FieldContainer(self.testData,
                                "1 km",
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1 m",
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1 m",
                                longname=self.longname + "bu",
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        #Test inequality of attributes
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname,
                                attributes={'set':True})
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        #Test inequality of dimensions
        field1 = FieldContainer(self.testData,
                                1,longname=self.longname,
                                shortname=self.shortname)
        field1.dimensions[0].data *= 10
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)

    def testEqualMasked(self):
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname + "bu",
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                "1 km",
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1000 m",
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertEqual(field1, field2)
        #necessary to test the != operator (__ne__)
        assert(not (field1 != field2))
        testMask2 = self.testMask.copy()
        testMask2[0, 2] = not self.testMask[0, 2]
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                mask=testMask2,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                mask=testMask2,
                                longname=self.longname + "bu",
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                "1 km",
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1000 m",
                                mask=testMask2,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        assert(field1 != field2) #necessary to test the != operator (__ne__)
        field1 = FieldContainer(self.testData,
                                "1 km",
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1 m",
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)
        field1 = FieldContainer(self.testData,
                                1,
                                mask=self.testMask,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                "1 m",
                                mask=self.testMask,
                                longname=self.longname + "bu",
                                shortname=self.shortname)
        self.assertNotEqual(field1, field2)

    def testAddition(self):
        field1 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal(sumField.data, field1.data + field2.data)
        self.assertEqual(1, sumField.unit)
        self.assertEqual(sumField.shortname,
                         u"%s + %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,
                                '1 m',
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                '2 m',
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal(sumField.data, field1.data / 2+field2.data)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s + %s" \
                             % (self.shortname, self.shortname))
        sumField = field2 + field1
        nt.assert_array_almost_equal(sumField.data,
                                     field1.data / 2 + field2.data)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname,
                         u"%s + %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,
                                '1 mm',
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal(sumField.data,
                                     field1.data / 2000 + field2.data)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname,
                         u"%s + %s" % (self.shortname, self.shortname))

    def testSubtraction(self):
        field1 = FieldContainer(numpy.random.randn(7, 13),
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(numpy.random.randn(7, 13),
                                1,
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal(sumField.data, field1.data - field2.data)
        self.assertEqual(1, sumField.unit)
        self.assertEqual(sumField.shortname,
                         u"%s - %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,
                                '1 m',
                                longname=self.longname,
                                shortname=self.shortname)
        field2 = FieldContainer(self.testData,
                                '2 m',
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal(sumField.data,
                                     field1.data / 2 - field2.data)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname,
                         u"%s - %s" % (self.shortname, self.shortname))
        sumField = field2 - field1
        nt.assert_array_almost_equal(sumField.data,
                                     field2.data - field1.data / 2)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname,
                         u"%s - %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,
                                '1 mm',
                                longname=self.longname,
                                shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal(sumField.data,
                                     field1.data / 2000 - field2.data)
        self.assertEqual(sumField.unit, Quantity('2 m'))
        self.assertEqual(sumField.shortname,
                         u"%s - %s" % (self.shortname, self.shortname))

class IsValidFieldContainer(unittest.TestCase):
    def setUp(self):
        self.field = FieldContainer(numpy.random.randn(7, 13),
                                    longname="voltage",
                                    shortname="U",
                                    unit="1V")

    def testWrongDimension(self):
        self.field.dimensions[0].data = self.field.dimensions[0].data[:-1]
        self.assertFalse(self.field.isValid())

    def testWrongDimensionNumber(self):
        self.field.dimensions.append(copy.deepcopy(self.field.dimensions[0]))
        self.assertFalse(self.field.isValid())
        self.field.dimensions = [self.field.dimensions[0]]
        self.assertFalse(self.field.isValid())

    def testWrongMask(self):
        shape = list(self.field.data.shape)
        self.field.mask = numpy.ones(shape)
        self.assertTrue(self.field.isValid())
        shape[0] = shape[0] + 1
        self.field.mask = numpy.ones(shape)
        self.assertFalse(self.field.isValid())

    def testWrongError(self):
        shape = list(self.field.data.shape)
        self.field.error = numpy.zeros(shape)
        self.assertTrue(self.field.isValid())
        shape[0] = shape[0] + 1
        self.field.error = numpy.ones(shape)
        self.assertFalse(self.field.isValid())

    def testDimension0HasSameShapeAsField(self):
        self.field.dimensions[0] = copy.deepcopy(self.field)
        self.assertFalse(self.field.isValid())

    def testDimension1HasSameShapeAsField(self):
        self.field.dimensions[1] = copy.deepcopy(self.field)
        self.assertFalse(self.field.isValid())


class SampleContainerTest(unittest.TestCase):
    def setUp(self):
        self.rows = 100
        self.intSample = FieldContainer(scipy.arange(0, self.rows),
                                        Quantity('1m'),
                                        #dimensions=INDEX,
                                        longname=u"Integer sample",
                                        shortname=u"i")
        self.intSample2 = FieldContainer(2 * scipy.arange(0, self.rows),
                                        Quantity('1m'),
                                        longname=u"Integer sample No2",
                                        shortname=u"i2")
        self.floatSample = FieldContainer(scipy.arange(self.rows / 2,
                                                       self.rows,
                                                       0.5),
                                          Quantity('1s'),
                                          longname=u"Float sample",
                                          shortname=u"t")
        self.shortFloatSample1 = FieldContainer(scipy.array([1., 2., 10.]),
                                          Quantity('1.0 s**2'),
                                          longname=u"Short Float sample 1",
                                          shortname=u"short1")
        self.shortFloatSample2 = FieldContainer(scipy.array([5., 10., 1.]),
                                          Quantity('1.0 kg * m'),
                                          longname=u"Short Float sample 2",
                                          shortname=u"short2")
        self.desc = scipy.dtype({'names':[u'i', u't'],
                                 'formats':[self.intSample.data.dtype,
                                            self.floatSample.data.dtype],
                                 'titles':[self.intSample.longname,
                                           self.floatSample.longname]})
        self.data = scipy.rec.fromarrays([self.intSample.data,
                                        self.floatSample.data],
                                       dtype=self.desc)
        self.longname = u"Toller Sample"
        self.shortname = u"phi"
        self.sampleContainer = SampleContainer([self.intSample,
                                                self.floatSample],
                                               self.longname,
                                               self.shortname)
        self.sampleContainerNeu = SampleContainer([self.intSample,
                                                   self.intSample2,
                                                self.floatSample,
                                                self.shortFloatSample1,
                                                self.shortFloatSample2],
                                               "New Sample",
                                               "NewSC")

    def runTest(self):
        return


class AlgebraSampleContainerTests(SampleContainerTest):

    def testNodeTransformer(self):
        from pyphant.core.AstTransformers import (ReplaceName, ReplaceOperator,
                                                  ReplaceCompare)
        rpn = ReplaceName(self.sampleContainer)
        import ast
        exprStr = 'col("i") / (col("t") + col("t"))'
        expr = compile(exprStr, "<TestCase>", 'eval', ast.PyCF_ONLY_AST)
        replacedExpr = rpn.visit(expr)
        print rpn.localDict
        print ast.dump(replacedExpr)
        rpc = ReplaceCompare(rpn.localDict)
        factorExpr = rpc.visit(replacedExpr)
        rpo = ReplaceOperator(rpn.localDict)
        factorExpr = rpo.visit(factorExpr)
        print ast.dump(factorExpr)

    def testCalcColumn(self):
        exprStr = 'col("i") / (col("t") + col("t")) + "1km/s"'
        column = self.sampleContainer.calcColumn(exprStr, 'v', 'velocity')
        #print self.sampleContainerNeu['i']
        #print self.sampleContainerNeu['t']
        #print self.sampleContainerNeu['i2']
        #print column
        exprStr = 'col("i") / (col("t") + col("t")) + "1km"'
        self.assertRaises(ValueError, self.sampleContainer.calcColumn,
                          exprStr, 'v', 'velocity')

    def testCalcColumnExplicit(self):
        exprStr = 'col("short1") * col("short2") - "10 kg * m * s**2"'
        columnOut = self.sampleContainerNeu.calcColumn(
            exprStr, 'Test1', 'Mult und Minus')
        #print(columnOut)
        columnCheck = FieldContainer(scipy.array([-5., 10., 0.]),
                                     unit='1 kg * m * s**2',
                                     shortname='Test1Check',
                                     longname='Test1Checken')
        #print(columnCheck.unit)
        #print(type(columnCheck.unit))
        checkIfDataEqual = columnOut.data == columnCheck.data
        if checkIfDataEqual.all() and columnOut.unit == columnCheck.unit:
            print('Explicit check No1 ok.')
        else:
            raise ValueError
        exprStr = '(col("short1") / col("short2") - "10.0 s**2/(kg*m)") ' + \
                  '> ("-5.0 s**2/(kg*m)")'
        columnOut = self.sampleContainerNeu.calcColumn(
            exprStr, 'Test1', 'Mult und Minus')
        #print(columnOut)
        #print(columnOut.unit)
        columnCheck = FieldContainer(scipy.array([False, False, True]),
                                     shortname='Test2Check',
                                     longname='Test2Checken')
        checkIfDataEqual = columnOut.data == columnCheck.data
        if checkIfDataEqual.all() and columnOut.unit == columnCheck.unit:
            print('Explicit check No2 ok.')
        else:
            raise ValueError
        exprStr = 'col("short1") * col("short2") - "10 kg * s**2"'
        self.assertRaises(
            ValueError, self.sampleContainerNeu.calcColumn, exprStr,
            'Test1assert', 'Test1AssertRaise')
        exprStr = '"1.0m" / "0.0m"'
        self.assertRaises(ZeroDivisionError,
                          self.sampleContainerNeu.calcColumn, exprStr,\
                                            'TestZero', 'Division by Zero')

    def testAlgebraPlus(self):
        from pyphant.core.DataContainer import FieldContainer
        expr = 'col("i") + col("i2") + "-10 m"'
        columnOut = self.sampleContainerNeu.calcColumn(
            expr, 'OutPlus', 'OutcomePlus')
        columnCheck = FieldContainer(3 * scipy.arange(0, self.rows) - 10,
                                unit='1 m',
                                longname="Outcome Check",
                                shortname="OC")
        checkIfDataEqual = columnOut.data == columnCheck.data
        if checkIfDataEqual.all() and columnOut.unit == columnCheck.unit:
            print("Adding works.")
        else:
            raise ValueError

    def testAlgebraMinus(self):
        from pyphant.core.DataContainer import FieldContainer
        expr = 'col("i") - col("i2") - "-10 km"'
        columnOut = self.sampleContainerNeu.calcColumn(
            expr, 'OutMinus', 'OutcomeMinus')
        columnCheck = FieldContainer(-1 * scipy.arange(0, self.rows) + 10000,
                                unit='1 m',
                                longname="Outcome Check",
                                shortname="OC")
        checkIfDataEqual = columnOut.data == columnCheck.data
        if checkIfDataEqual.all() and columnOut.unit == columnCheck.unit:
            print("Subtracting works.")
        else:
            raise ValueError

    def testAlgebraMult(self):
        from pyphant.core.DataContainer import FieldContainer
        expr = 'col("i") * col("i") * 0.5'
        columnOut = self.sampleContainerNeu.calcColumn(
            expr, 'OutMult', 'OutcomeMult')
        columnCheckData = scipy.array(
            map(lambda x: x ** 2 * 0.5, scipy.arange(0, self.rows)))
        columnCheck = FieldContainer(columnCheckData,
                                unit='1 m**2',
                                longname="Outcome Check",
                                shortname="OC")
        checkIfDataEqual = columnOut.data == columnCheck.data
        if checkIfDataEqual.all() and columnOut.unit == columnCheck.unit:
            print("Multiplying works.")
        else:
            raise ValueError

    def testAlgebraDiv(self):
        from pyphant.core.DataContainer import FieldContainer
        expr = 'col("i") / 2.'
        expr2 = '(col("i") + "1 m") / (col("i") + "1 m")'
        columnOut = self.sampleContainerNeu.calcColumn(
            expr, 'OutDiv', 'OutcomeDiv')
        #print(columnOut)
        columnOut2 = self.sampleContainerNeu.calcColumn(
            expr2, 'OutDiv2', 'OutcomeDiv2')
        #print(columnOut.unit)
        #columnCheckData = scipy.array([1 for i in range(0,self.rows)])
        columnCheckData = 0.5 * scipy.arange(0., float(self.rows))
        columnCheckData2 = scipy.array([1. for i in range(0, self.rows)])
        columnCheck = FieldContainer(columnCheckData,
                                unit='1 m',
                                longname="Outcome Check",
                                shortname="OC")
        columnCheck2 = FieldContainer(columnCheckData2,
                                unit='1.0',
                                longname="Outcome Check",
                                shortname="OC")
        checkIfDataEqual = columnOut.data == columnCheck.data
        checkIfDataEqual2 = columnOut2.data == columnCheck2.data
        if checkIfDataEqual.all() and checkIfDataEqual2.all() \
               and columnOut.unit == columnCheck.unit:
            print("Dividing works.")
        else:
            raise ValueError

    def testDimensions(self):
        fc1 = FieldContainer(numpy.array([4, 5, 6]), unit=Quantity('1 m'),
                             dimensions=[FieldContainer(
                                 numpy.array([1, 2, 3]), unit=Quantity('1 s'))],
                             shortname='s1')
        fc2 = FieldContainer(numpy.array([1, 2, 3]), unit=Quantity('1 km'),
                             dimensions=[FieldContainer(
                                 numpy.array([10, 20, 30]),
                                 unit=Quantity('0.1 s'))],
                             shortname='s2')
        sc = SampleContainer(columns=[fc1, fc2])
        expr = "col('s1') + col('s2')"
        dims = sc.calcColumn(expr, 'Add', 'a').dimensions
        self.assertEqual(dims, fc1.dimensions)
        self.assertEqual(dims, fc2.dimensions)
        fc2.dimensions[0].unit = Quantity('0.11 s')
        self.assertRaises(ValueError, sc.calcColumn, expr, 'Add', 'a')


class CommonSampleContainerTests(SampleContainerTest):
    def testLabeling(self):
        self.assertEqual(self.sampleContainer.label,
                         "%s %s" % (self.longname,self.shortname))

    def testDeepcopy(self):
        sample = self.sampleContainer
        copiedSample = copy.deepcopy(sample)
        self.assertEqual(sample, copiedSample)
        sample.seal()
        copiedSample.seal()
        self.assertEqual(sample, copiedSample)
        #equal because only real data is considered:
        self.assertEqual(sample.hash, copiedSample.hash)
        #unique due to timestamp in dimension ids:
        self.assertNotEqual(sample.id, copiedSample.id)

    def testSeal(self):
        sample = self.sampleContainer
        sample.seal()
        self.assertNotEqual(sample.id, None)
        self.assertNotEqual(sample.hash, None)
        try:
            sample.data=scipy.array([1, 2, 3])
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not "
                      "prohibited.")
        try:
            sample['i'].data[0] = 4
        except RuntimeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not "
                      "prohibited.")

    def testSingleSample(self):
        #string = numpy.rec.fromrecords([(s,) for s in [u'Hello',u'World!',u'Bäh!']])
#        strings =
        uField = FieldContainer(scipy.array([u'Hello', u'World!', u'Bäh!']),
                                longname=u'Text',
                                shortname='\gamma')
        #was: table  = SampleContainer([uField]). Intent unclear:
        table = SampleContainer([uField])

    def testStringSample(self):
        #string = numpy.rec.fromrecords([(s,) for s in [u'Hello',u'World!',u'Bäh!']])
#        strings =
        uField = FieldContainer(scipy.array([u'Hello', u'World!', u'Bäh!']),
                                longname=u'Text',
                                shortname='\gamma')
        sample = SampleContainer([uField])
        sample.seal()
        #print sample,sample.data

    def testEqual(self):
        #Test Equality
        sample1 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname)
        sample2 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname)
        self.assertEqual(sample1, sample2)
        #Test inequality due to different longnames
        sample1 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname)
        sample2 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname + 'bu',
                                  shortname=self.shortname)
        self.assertNotEqual(sample1, sample2)
        #Test inequality to due different shortnames
        sample1 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname)
        sample2 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname + 'a')
        self.assertNotEqual(sample1, sample2)
        #Test inequality of attributes
        sample1 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname)
        sample2 = SampleContainer([self.intSample, self.floatSample],
                                  longname=self.longname,
                                  shortname=self.shortname,
                                  attributes={'set':True})
        self.assertNotEqual(sample1, sample2)


class SampleContainerSlicingTests(SampleContainerTest):
    def setUp(self):
        SampleContainerTest.setUp(self)
        time_data = numpy.array([10.0, 20.0, 30.0, 5.0, 9000.0])
        time_error = numpy.array([1.0, 2.0, 3.0, .5, 900.0])
        time_unit = Quantity('2s')
        time_FC = FieldContainer(time_data, time_unit, time_error,
                                 None, None,
                                 "Zeit", "t",
                                 None, False)
        length_data = numpy.array([-20.0, 0.0, 20.0, 10.0, 5.5])
        length_error = numpy.array([2.0, 0.1, 2.0, 1.0, .5])
        length_unit = Quantity('1000m')
        length_FC = FieldContainer(length_data, length_unit, length_error,
                                   None, None,
                                   "Strecke", "l",
                                   None, False)
        temperature_data = numpy.array([[10.1, 10.2, 10.3],
                                        [20.1, 20.2, 20.3],
                                        [30.1, 30.2, 30.3],
                                        [40.1, 40.2, 40.3],
                                        [50.1, 50.2, 50.3]])
        temperature_error = numpy.array([[0.1, 0.2, 0.3],
                                         [1.1, 1.2, 1.3],
                                         [2.1, 2.2, 2.3],
                                         [3.1, 3.2, 3.3],
                                         [4.1, 4.2, 4.3]])
        temperature_unit = Quantity('1mK')
        temperature_FC = FieldContainer(temperature_data,
                                        temperature_unit,
                                        temperature_error,
                                        None, None,
                                        "Temperatur", "T",
                                        None, False)
        self.sc2d = SampleContainer([length_FC, temperature_FC, time_FC],
                                    "Test Container", "TestC")
        self.sc2d["t"].dimensions[0].unit = Quantity('1m')
        self.sc2d["t"].dimensions[0].data = numpy.array([-20, -10, 0, 10, 20])
        self.sc2d["l"].dimensions[0].unit = Quantity('5m')
        self.sc2d["l"].dimensions[0].data = numpy.array([-4, -2, 0, 2, 4])
        self.sc2d["T"].dimensions[0].unit = Quantity('2m')
        self.sc2d["T"].dimensions[0].data = numpy.array([-10, -5, 0, 5, 10])
        self.sc2d["T"].dimensions[1].unit = Quantity('10nm')
        self.sc2d["T"].dimensions[1].data = numpy.array([-1, 0, 1])

    #purely one dimensional Tests:
    def testConsistancy(self):
        result1 = self.sampleContainer.filter(
            '"20m" < col("i") and "80m" > col("i")')
        result2 = self.sampleContainer.filter('"20m" < col("i") < "80m"')
        self.assertEqual(result1[0], result2[0])
        self.assertEqual(result1[1], result2[1])

    def testSimpleUnicodeExpression(self):
        result = self.sampleContainer.filter(u'"50m" <= col("i") < "57m"')
        self.assertEqual(len(result.columns), 2)
        self.assertEqual(len(result[0].data), 7)
        self.assertEqual(len(result[1].data), 7)
        expected = self.sampleContainer["i"][50:57]
        expected.attributes={}
        result.attributes={}
        self.assertEqual(result[0], expected)
        expected = self.sampleContainer["t"][50:57]
        expected.attributes={}
        result.attributes={}
        self.assertEqual(result[1], expected)

    def testANDExpression(self):
        result = self.sampleContainer.filter(
            'col("i") >= "20m" and col("t") <= "98.5s"')
        expectedi = self.sampleContainer["i"][20:98]
        expectedt = self.sampleContainer["t"][20:98]
        expectedi.attributes = {}
        expectedt.attributes = {}
        result[0].attributes = {}
        result[1].attributes = {}
        self.assertEqual(result[0], expectedi)
        self.assertEqual(result[1], expectedt)

    #tests involving 2 dimensional FieldContainers:
    def _compareExpected(self, expression, ind):
        indices = numpy.array(ind)
        result = self.sc2d.filter(expression)
        expectedSC = copy.deepcopy(self.sc2d)
        for FC in expectedSC:
            FC.data = FC.data[indices]
            FC.error = FC.error[indices]
            FC.dimensions[0].data = FC.dimensions[0].data[indices]
        self.assertEqual(result, expectedSC)
        return result

    def testEmpty2dExpression(self):
        result = self.sc2d.filter('')
        self.assertEqual(result, self.sc2d)

    def testAtomar2dExpressions(self):
        self._compareExpected('col("t") <= "40.0s"',
                              [True, True, False, True, False])
        self._compareExpected('col("l") < "10000m"',
                              [True, True, False, False, True])
        self._compareExpected('col("Zeit") >= "20.0s"',
                              [True, True, True, False, True])
        self._compareExpected('col("l") > "5500m"',
                              [False, False, True, True, False])
        self._compareExpected('col("t") == "18000s"',
                              [False, False, False, False, True])
        self._compareExpected('col("Strecke") != "20000m"',
                              [True, True, False, True, True])

    def testNot2dExpression(self):
        self._compareExpected('not col("t") == "10s"',
                              [True, True, True, False, True])

    def testAnd2dExpression(self):
        self._compareExpected(
            'col("Zeit") == "60s" and "20000m" == col("Strecke")',
            [False, False, True, False, False])

    def testMultiAnd2dExpression(self):
        self._compareExpected(
            "col('l') >= '0 km' and col('l') < '20 km' and col('t') <= '60s'",
            [False, True, False, True, False])

    def testOr2dExpression(self):
        self._compareExpected(
            'col("Zeit") < "60s" or col("Strecke") == "5500m"',
            [True, True, False, True, True])

    def testMultiOr2dExpression(self):
        self._compareExpected(
            "col('t') == '20s' or col('l') == '0 km' or col('t') > '1000.2 s'",
            [True, True, False, False, True]
            )

    def testMultipleCompareOpPrecedence2dExpression(self):
        self._compareExpected('not "0m" <= col("l") <= "10000m"',
                              [True, False, True, False, False])

    def testColumnToColumn2dExpression(self):
        self._compareExpected('col("l") == col("Strecke")',
                              [True, True, True, True, True])
        self._compareExpected('col("t") != col("Zeit")',
                              [False, False, False, False, False])

    def testIncompatibleDimensionsExpression(self):
        fc1 = FieldContainer(numpy.array([1, 2, 3]),
                             dimensions=[FieldContainer(numpy.array([4, 5, 6]),
                                                        unit=Quantity('1m'))],
                             shortname='t1')
        fc2 = copy.deepcopy(fc1)
        fc2.dimensions[0].data[0] = 4.01
        fc2.shortname = 't2'
        incompatibleSC = SampleContainer(columns=[fc1, fc2])
        self.assertRaises(ValueError, incompatibleSC.filter,
                          "col('t1') > col('t2')")


class FieldContainerRescaling(unittest.TestCase):
    def setUp(self):
        self.testData = scipy.array([[0,1,2],[3,4,5],[6,7,8]])
        self.longname = u"Sampled Data"
        self.shortname = u"I\\omega"
        self.unit = Quantity('3.14 m')

    def testRescaleUnitless(self):
        field = FieldContainer(copy.deepcopy(self.testData),
                               1,
                               longname=self.longname,
                               shortname=self.shortname)
        nt.assert_array_equal(self.testData,
                              field.data,
                              'Unauthorized rescaling.')
        field = FieldContainer(copy.deepcopy(self.testData),
                               1,
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        nt.assert_array_equal(self.testData,
                              field.data,
                              "Rescale option shouldn't do anything for "
                              "unitless fields.")

    def testRescaleBaseUnitsFloats(self):
        field = FieldContainer(copy.deepcopy(self.testData).astype('f'),
                               '1 cm**2/mm',
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        nt.assert_array_equal(self.testData,field.data,
                              'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),
                         'dm',
                         'Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleFloats(self):
        field = FieldContainer(100 * copy.deepcopy(self.testData).astype('f'),
                               '10 muA',
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        nt.assert_array_almost_equal(self.testData,
                                     field.data,5,
                                     'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),
                         'mA',
                         'Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleFloatsMeter(self):
        field = FieldContainer(100 * copy.deepcopy(self.testData).astype('f'),
                               '1 cm**2/mm',
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        nt.assert_array_almost_equal(10 * self.testData,
                                     field.data,
                                     5,
                                     'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),
                         'm',
                         'Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleBaseUnitsInteger(self):
        field = FieldContainer(copy.deepcopy(self.testData),
                               '1 cm**2/mm',
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        nt.assert_array_equal(self.testData,
                              field.data,
                              'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),
                         'dm',
                         'Wrong baseunit: %s.' % field.unit.unit.name())

    def testUnitInteger(self):
        field = FieldContainer(copy.deepcopy(self.testData),
                               unit=self.unit,
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        self.assertEqual(field.unit,
                         self.unit,
                         "An integer field should not be rescaled, but should "
                         "hold the normation constant in its unit.")

    def testDimensionsRescaling(self):
        """
        Option rescale=True should also rescale the dimensions of the
        FieldContainer.
        """
        dim = [FieldContainer(1000 * scipy.linspace(0, 1, 3),
                              unit='1 nm',
                              longname="Axis %s" % axis,
                              shortname=axis) for axis in ['x','y']]
        field = FieldContainer(copy.deepcopy(self.testData),
                               dimensions=dim,
                               unit=self.unit,
                               longname=self.longname,
                               shortname=self.shortname,
                               rescale=True)
        for dim in [0,1]:
            axisUnit = field.dimensions[dim].unit
            self.assertEqual(axisUnit.unit.name(), 'mum')

class FieldContainerSlicing1d(unittest.TestCase):
    def setUp(self):
        self.field1d = FieldContainer(numpy.linspace(0.1, 1, 10),
                                      longname="voltage",
                                      shortname="U",
                                      unit="1V")
    def testSingleIndex(self):
        section = self.field1d[0]
        afoot = FieldContainer(numpy.array([0.1]),
                               longname="afoot",
                               shortname="U",
                               unit="1V",
                               dimensions=[],
                               attributes={u'Index':(u'i', 0)})
        assertEqual(section, afoot)

    def testRegionIndex(self):
        section = self.field1d[1:4]
        afoot = FieldContainer(numpy.linspace(0.2, 0.4, 3),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1, 3, 3)
        self.assertEqual(section, afoot)
        section = self.field1d[1:-1]
        afoot = FieldContainer(numpy.linspace(0.2, 0.9, 8),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1, 8, 8)
        self.assertEqual(section, afoot)

    def testCommaSeparated(self):
        section = self.field1d[[1, 3, 7], ]
        afoot = FieldContainer(numpy.array([0.2, 0.4, 0.8]),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.array([1, 3, 7])
        self.assertEqual(section, afoot)
        section = self.field1d[[[1, 3, 7]]]
        self.assertEqual(section, afoot)

    def testRegionIndexUnit(self):
        f = self.field1d.dimensions[0]
        mask = slice(3, 7)
        afoot = FieldContainer(self.field1d.data[mask],
                               dimensions=[f[mask]],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        self.assertRaises(NotImplementedError,
                          self.field1d.__getitem__,
                          "0.4:0.6")
        section = self.field1d["3:7"]
        assertEqual(section, afoot)


class FieldContainerSlicing1dDim(FieldContainerSlicing1d):
    def setUp(self):
        super(FieldContainerSlicing1dDim, self).setUp()
        self.xDim = FieldContainer(numpy.linspace(0.3,
                                                  0.7,
                                                  self.field1d.data.shape[0]),
                                   longname="current",
                                   shortname="I",
                                   unit="1A")
        self.field1d.dimensions[0] = self.xDim

    def testSingleIndex(self):
        section = self.field1d[0]
        afoot = FieldContainer(numpy.array([0.1]),
                               longname="afoot",
                               shortname="U",
                               unit="1V",
                               dimensions=[self.xDim[0]],
                               attributes={u'current':\
                                           (u'I', Quantity("0.3A"))})
        assertEqual(section, afoot)

    def testRegionIndex(self):
        section = self.field1d[1:4]
        afoot = FieldContainer(numpy.linspace(0.2, 0.4, 3),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.xDim[1:4]
        self.assertEqual(section, afoot)
        section = self.field1d[1:-1]
        afoot = FieldContainer(numpy.linspace(0.2, 0.9, 8),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.xDim[1:-1]
        self.assertEqual(section, afoot)

    def testCompleteRightOpenIntervall(self):
        dim = self.xDim
        intStart = dim.data.min() * dim.unit
        intEnd = dim.data.max() * dim.unit
        unitname = dim.unit.unit.name()
        section = self.field1d["%.4f%s:%.4f%s" % (intStart.value,
                                                  unitname,
                                                  intEnd.value,
                                                  unitname)]
        afoot = FieldContainer(numpy.linspace(0.1, 0.9, 9),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.xDim[0:-1]
        self.assertEqual(section, afoot)

    def testCompleteIntervall(self):
        dim = self.xDim
        intStart = dim.data.min() * dim.unit
        intEnd = dim.data.max() * dim.unit * 1.001
        unitname = dim.unit.unit.name()
        argument = "%.4f%s:%.4f%s" % (intStart.value,
                                      unitname,
                                      intEnd.value,
                                      unitname)
        section = self.field1d[argument]
        self.assertEqual(section, self.field1d)

    def testCommaSeparated(self):
        section = self.field1d[[1, 3, 7], ]
        afoot = FieldContainer(numpy.array([0.2, 0.4, 0.8]),
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.xDim[[1, 3, 7], ]
        self.assertEqual(section, afoot)
        section = self.field1d[[[1, 3, 7]]]
        self.assertEqual(section, afoot)

    def testRegionIndexUnit(self):
        f = self.field1d.dimensions[0]
        mask = slice(3, 7)
        afoot = FieldContainer(self.field1d.data[mask],
                               dimensions=[f[mask]],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        section = self.field1d["0.4:0.6A"]
        assertEqual(section, afoot)
        section = self.field1d["400mA:0.6A"]
        assertEqual(section, afoot)

    def testRegionIndexUnitExtendedLeftBoundary(self):
        f = self.field1d.dimensions[0]
        mask = slice(0, 7)
        afoot = FieldContainer(self.field1d.data[mask],
                               dimensions=[f[mask]],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        section = self.field1d["0.:0.6A"]
        assertEqual(section, afoot)
        section = self.field1d["0mA:0.6A"]
        assertEqual(section, afoot)
        section = self.field1d["300mA:0.6A"]
        assertEqual(section, afoot)

    def testRegionIndexUnitRightBoundary(self):
        f = self.field1d.dimensions[0]
        mask = slice(3, None)
        afoot = FieldContainer(self.field1d.data[mask],
                               dimensions=[f[mask]],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        section = self.field1d["0.4:1A"]
        assertEqual(section, afoot)
        section = self.field1d["0.4A:1000mA"]
        assertEqual(section, afoot)
        section = self.field1d["0.4A:700mA"]
        assertEqual(section, afoot)


class FieldContainerSlicing2d(unittest.TestCase):
    def setUp(self):
        l = numpy.linspace(0, 0.9, 10)
        m = numpy.meshgrid(l, l * 10)
        self.field2d = FieldContainer(m[0] + m[1],
                                      longname="voltage",
                                      shortname="U",
                                      unit="1V")

    def testSingleIndex(self):
        section = self.field2d[0]
        afoot = FieldContainer(numpy.linspace(0, 0.9, 10),
                               longname="voltage",
                               shortname="U",
                               unit="1V",
                               attributes={u'Index':(u'j', 0)})
        self.assertTrue(section.isValid())
        self.assertEqual(section, afoot)

    def testRegionIndex(self):
        section = self.field2d[1:4]
        afoot = FieldContainer(self.field2d.data[1:4],
                               longname="afoot",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1, 3, 3)
        self.assertEqual(section, afoot)
        section = self.field2d[1:-1]
        afoot = FieldContainer(self.field2d.data[1:-1],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1, 8, 8)
        self.assertEqual(section, afoot)

    def testCommaSeparated(self):
        section = self.field2d[[1, 3, 7], ]
        afoot = FieldContainer(self.field2d.data[[1, 3, 7], ],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0].data = numpy.array([1, 3, 7])
        self.assertEqual(section, afoot)
        section = self.field2d[[[1, 3, 7]]]
        self.assertEqual(section, afoot)


class FieldContainerSlicing2dDim(FieldContainerSlicing2d):
    def setUp(self):
        super(FieldContainerSlicing2dDim, self).setUp()
        self.xDim = FieldContainer(numpy.linspace(0.3,
                                                  0.7,
                                                  self.field2d.data.shape[0]),
                                   longname="current",
                                   shortname="I",
                                   unit="1A")
        self.yDim = FieldContainer(numpy.linspace(30,
                                                  70,
                                                  self.field2d.data.shape[0]),
                                   longname="position",
                                   shortname="p",
                                   unit="1cm")
        self.field2d.dimensions = [self.yDim, self.xDim]

    def testSingleIndex(self):
        section = self.field2d[0]
        afoot = FieldContainer(numpy.linspace(0, 0.9, 10),
                               longname="voltage",
                               shortname="U",
                               unit="1V",
                               attributes={u'position':\
                                               (u'p',Quantity("30cm"))},
                               dimensions=[self.xDim])
        self.assertTrue(section.isValid())
        self.assertEqual(section, afoot)

    def testRegionIndex(self):
        section = self.field2d[1:4]
        afoot = FieldContainer(self.field2d.data[1:4],
                               longname="afoot",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim[1:4]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section, afoot)
        section = self.field2d[1:-1]
        afoot = FieldContainer(self.field2d.data[1:-1],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim[1:-1]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section, afoot)

    def testCommaSeparated(self):
        section = self.field2d[[1, 3, 7], ]
        afoot = FieldContainer(self.field2d.data[[1, 3, 7], ],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim[[1, 3, 7], ]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section, afoot)
        section = self.field2d[[[1, 3, 7]]]
        self.assertEqual(section, afoot)

    def testRegionIndexUnit(self):
        section = self.field2d["4:6dm"]
        afoot = FieldContainer(self.field2d.data[3:7],
                               longname="afoot",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim[3:7]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section, afoot)

    def testRegionIndexWrongUnit(self):
        self.assertRaises(TypeError, self.field2d.__getitem__, "4:6A")

    def test2FoldRegionIndexUnit(self):
        section = self.field2d["4:6dm", "4e-1:.6A"]
        afoot = FieldContainer(self.field2d.data[3:7, 3:7],
                               longname="afoot",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim[3:7]
        afoot.dimensions[1] = self.xDim[3:7]
        self.assertEqual(section, afoot)

    def test2ndAxisRegionIndexUnit(self):
        section = self.field2d[:, "4e-1:.6A"]
        afoot = FieldContainer(self.field2d.data[:, 3:7],
                               longname="afoot",
                               shortname="U",
                               unit="1V")
        afoot.dimensions[0] = self.yDim
        afoot.dimensions[1] = self.xDim[3:7]
        self.assertEqual(section, afoot)


if __name__ == "__main__":
    #suite = unittest.TestLoader().loadTestsFromTestCase(IsValidFieldContainer)
    #unittest.TextTestRunner().run(suite)
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FieldContainerSlicing1dDim))
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
