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

u"""Provides unittest classes FieldContainerTestCase, SampleContainerTest.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import unittest
import pkg_resources
pkg_resources.require("Pyphant")

import scipy
import copy
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity
from pyphant.core.DataContainer import (INDEX, generateIndex,
                                        FieldContainer,SampleContainer,DataContainer,
                                        assertEqual)
import numpy.testing as nt
import numpy

class DataContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DataContainer('variable','v')
        self.dc0 = DataContainer('variable','v_0')

    def testNoSubscriptPersistent(self):
        result = self.dc.appendSubscript('i')
        self.assertEqual(result,'v_{i}')
        self.assertEqual(self.dc.shortname,'v_{i}')

    def testSubscriptPersistent(self):
        result = self.dc0.appendSubscript('i')
        self.assertEqual(result,'v_{0,i}')
        self.assertEqual(self.dc0.shortname,'v_{0,i}')

    def testNoSubscriptNotPersistent(self):
        result = self.dc.appendSubscript('i',persistent=False)
        self.assertEqual(result,'v_{i}')
        self.assertEqual(self.dc.shortname,'v')

    def testSubscriptNotPersistent(self):
        result = self.dc0.appendSubscript('i',persistent=False)
        self.assertEqual(result,'v_{0,i}')
        self.assertEqual(self.dc0.shortname,'v_0')

    def testDefaultAttribute(self):
        "Checking if the default attribute has correctly been set to an empty dictionary."
        self.assertEqual(self.dc.attributes,{},'Expected an empty dictionary as attribute, but found %s.' % self.dc.attributes )

class FieldContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.testData = scipy.array([[0.,1.,2.],[3.,4.,5.],[6.,7.,8.]])
        self.testMask = self.testData > 5
        self.longname = u"Sampled Data"
        self.shortname = u"I\\omega"
        self.unit = PhysicalQuantity('3.14 m')

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
        field = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        self.assertEqual(field.label,"%s $%s(i,j)$ / a.u." % (self.longname,self.shortname))
        field = FieldContainer(self.testData,self.unit,longname=self.longname,shortname=self.shortname)
        self.assertEqual(field.label,"%s $%s(i,j)$ / %s" % (self.longname,self.shortname,self.unit))

    def testSeal(self):
        field = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field.seal()
        self.assertNotEqual(field.id, None)
        self.assertNotEqual(field.hash, None)
        try:
            field.data=scipy.array([1,2,3])
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not prohibited.")
        try:
            field.data[1]=4
        except RuntimeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not prohibited.")
        try:
            field.dimensions[0]=copy.deepcopy(field)
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer's dimension was not prohibited.")

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
        field = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        copiedField=copy.deepcopy(field)
        self.assertEqual(field, copiedField)
        field.seal()
        copiedField.seal()
        self.assertEqual(field, copiedField)
        self.assertEqual(field.hash, copiedField.hash) #equal because only real data is considered
        self.assertNotEqual(field.id, copiedField.id) #unique due to timestamp in dimension ids

    def testEqual(self):
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        self.assertEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,longname=self.longname+"bu",shortname=self.shortname)
        self.assertEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname+'a')
        self.assertEqual( field1, field2 )
        field1 = FieldContainer(self.testData,"1 km",longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1000 m",longname=self.longname,shortname=self.shortname)
        self.assertEqual( field1, field2 )
        assert( not (field1 != field2) ) #necessary to test the != operator (__ne__)
        field1 = FieldContainer(self.testData,"1 km",longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1 m",longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1 m",longname=self.longname+"bu",shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        #Test inequality of attributes
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname,attributes={'set':True})
        field2 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        #Test inequality of dimensions
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field1.dimensions[0].data *= 10
        field2 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )

    def testEqualMasked(self):
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        self.assertEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname+"bu",shortname=self.shortname)
        self.assertEqual( field1, field2 )
        field1 = FieldContainer(self.testData,"1 km",mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1000 m",mask=self.testMask,longname=self.longname,shortname=self.shortname)
        self.assertEqual( field1, field2 )
        assert( not (field1 != field2) ) #necessary to test the != operator (__ne__)
        testMask2 = self.testMask.copy()
        testMask2[0,2] = not self.testMask[0,2]
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,mask=testMask2,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,mask=testMask2,longname=self.longname+"bu",shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,"1 km",mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1000 m",mask=testMask2,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        assert( field1 != field2 ) #necessary to test the != operator (__ne__)
        field1 = FieldContainer(self.testData,"1 km",mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1 m",mask=self.testMask,longname=self.longname,shortname=self.shortname)
        self.assertNotEqual( field1, field2 )
        field1 = FieldContainer(self.testData,1,mask=self.testMask,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,"1 m",mask=self.testMask,longname=self.longname+"bu",shortname=self.shortname)
        self.assertNotEqual( field1, field2 )

    def testAddition(self):
        field1 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,1,longname=self.longname,shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal( sumField.data, field1.data+field2.data )
        self.assertEqual(1, sumField.unit)
        self.assertEqual(sumField.shortname, u"%s + %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,'1 m',longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,'2 m',longname=self.longname,shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal( sumField.data, field1.data/2+field2.data )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s + %s" % (self.shortname, self.shortname))
        sumField = field2 + field1
        nt.assert_array_almost_equal( sumField.data, field1.data/2+field2.data )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s + %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,'1 mm',longname=self.longname,shortname=self.shortname)
        sumField = field1 + field2
        nt.assert_array_almost_equal( sumField.data, field1.data/2000+field2.data )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s + %s" % (self.shortname, self.shortname))

    def testSubtraction(self):
        field1 = FieldContainer(numpy.random.randn(7,13),1,longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(numpy.random.randn(7,13),1,longname=self.longname,shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal( sumField.data, field1.data-field2.data)
        self.assertEqual(1, sumField.unit)
        self.assertEqual(sumField.shortname, u"%s - %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,'1 m',longname=self.longname,shortname=self.shortname)
        field2 = FieldContainer(self.testData,'2 m',longname=self.longname,shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal( sumField.data, field1.data/2-field2.data )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s - %s" % (self.shortname, self.shortname))
        sumField = field2 - field1
        nt.assert_array_almost_equal( sumField.data, field2.data-field1.data/2 )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s - %s" % (self.shortname, self.shortname))
        field1 = FieldContainer(self.testData,'1 mm',longname=self.longname,shortname=self.shortname)
        sumField = field1 - field2
        nt.assert_array_almost_equal( sumField.data, field1.data/2000-field2.data )
        self.assertEqual(sumField.unit, PhysicalQuantity('2 m'))
        self.assertEqual(sumField.shortname, u"%s - %s" % (self.shortname, self.shortname))

class IsValidFieldContainer(unittest.TestCase):
    def setUp(self):
        self.field = FieldContainer(numpy.random.randn(7,13),
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
        shape[0] = shape[0]+1
        self.field.mask = numpy.ones(shape)
        self.assertFalse(self.field.isValid())

    def testWrongError(self):
        shape = list(self.field.data.shape)
        self.field.error = numpy.zeros(shape)
        self.assertTrue(self.field.isValid())
        shape[0] = shape[0]+1
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
        self.rows=100
        self.intSample = FieldContainer(scipy.arange(0,self.rows),
                                        PhysicalQuantity('1m'),
                                        #dimensions=INDEX,
                                        longname=u"Integer sample",
                                        shortname=u"i")
        self.floatSample = FieldContainer(scipy.arange(self.rows/2,self.rows,0.5),
                                          PhysicalQuantity('1s'),
                                          longname=u"Float sample",
                                          shortname=u"t")
        self.desc = scipy.dtype({'names':[u'i', u't'], 'formats':[self.intSample.data.dtype,
                                                                  self.floatSample.data.dtype],
                                 'titles':[self.intSample.longname, self.floatSample.longname]})
        self.data=scipy.rec.fromarrays([self.intSample.data, self.floatSample.data], dtype=self.desc)
        self.longname=u"Toller Sample"
        self.shortname=u"phi"
        self.sampleContainer=SampleContainer([self.intSample, self.floatSample], self.longname, self.shortname)
        
    def runTest(self):
        return

class CommonSampleContainerTests(SampleContainerTest):
    def testLabeling(self):
        self.assertEqual(self.sampleContainer.label,"%s %s" % (self.longname,self.shortname))

    def testDeepcopy(self):
        sample = self.sampleContainer
        copiedSample=copy.deepcopy(sample)
        self.assertEqual(sample, copiedSample)
        sample.seal()
        copiedSample.seal()
        self.assertEqual(sample, copiedSample)
        self.assertEqual(sample.hash, copiedSample.hash) #equal because only real data is considered
        self.assertNotEqual(sample.id, copiedSample.id) #unique due to timestamp in dimension ids

    def testSeal(self):
        sample = self.sampleContainer
        sample.seal()
        self.assertNotEqual(sample.id, None)
        self.assertNotEqual(sample.hash, None)
        try:
            sample.data=scipy.array([1,2,3])
        except TypeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not prohibited.")
        try:
            sample['i'].data[0]=4
        except RuntimeError, e:
            pass
        else:
            self.fail("Modification of sealed FieldContainer was not prohibited.")

    def testSingleSample(self):
        #string = numpy.rec.fromrecords([(s,) for s in [u'Hello',u'World!',u'Bäh!']])
#        strings =
        uField = FieldContainer(scipy.array([u'Hello',u'World!',u'Bäh!']),longname=u'Text',shortname='\gamma')
        table  = SampleContainer([uField]) #was: table  = SampleContainer([uField]). Intent unclear

    def testStringSample(self):
        #string = numpy.rec.fromrecords([(s,) for s in [u'Hello',u'World!',u'Bäh!']])
#        strings =
        uField = FieldContainer(scipy.array([u'Hello',u'World!',u'Bäh!']),longname=u'Text',shortname='\gamma')
        sample = SampleContainer([uField])
        sample.seal()
        #print sample,sample.data

    def testEqual(self):
        #Test Equality
        sample1 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname)
        sample2 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname)
        self.assertEqual( sample1, sample2 )
        #Test inequality due to different longnames
        sample1 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname)
        sample2 = SampleContainer([self.intSample,self.floatSample],longname=self.longname+'bu',shortname=self.shortname)
        self.assertNotEqual( sample1, sample2 )
        #Test inequality to due different shortnames
        sample1 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname)
        sample2 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname+'a')
        self.assertNotEqual( sample1, sample2 )
        #Test inequality of attributes
        sample1 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname)
        sample2 = SampleContainer([self.intSample,self.floatSample],longname=self.longname,shortname=self.shortname,attributes={'set':True})
        self.assertNotEqual( sample1, sample2)


class SampleContainerSlicingTests(SampleContainerTest):
    #TODO: Write more tests with more complicated expressions
    def testConsistancy(self):
        result1 = self.sampleContainer.filter('20m < "i" and 80m > "i"')
        result2 = self.sampleContainer.filter('20m < "i" < 80m')
        self.assertEqual(result1[0], result2[0])
        self.assertEqual(result1[1], result2[1])
    
    def testSimpleExpression(self):
        result = self.sampleContainer.filter('50m <= "i" < 57m')
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
        result = self.sampleContainer.filter('"i" >= 20m and "t" <= 98.5s')
        expectedi = self.sampleContainer["i"][20:98]
        expectedt = self.sampleContainer["t"][20:98]
        expectedi.attributes = {}
        expectedt.attributes = {}
        result[0].attributes = {}
        result[1].attributes = {}
        self.assertEqual(result[0], expectedi)
        self.assertEqual(result[1], expectedt)


class FieldContainerRescaling(unittest.TestCase):
    def setUp(self):
        self.testData = scipy.array([[0,1,2],[3,4,5],[6,7,8]])
        self.longname = u"Sampled Data"
        self.shortname = u"I\\omega"
        self.unit = PhysicalQuantity('3.14 m')

    def testRescaleUnitless(self):
        field = FieldContainer(copy.deepcopy(self.testData),1,longname=self.longname,
                               shortname=self.shortname)
        nt.assert_array_equal(self.testData,field.data,'Unauthorized rescaling.')
        field = FieldContainer(copy.deepcopy(self.testData),1,longname=self.longname,
                               shortname=self.shortname,rescale=True)
        nt.assert_array_equal(self.testData,field.data,
                              "Rescale option shouldn't do anything for unitless fields.")

    def testRescaleBaseUnitsFloats(self):
        field = FieldContainer(copy.deepcopy(self.testData).astype('f'),
                               '1 cm**2/mm',longname=self.longname,
                               shortname=self.shortname,rescale=True)
        nt.assert_array_equal(self.testData,field.data,'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),'dm','Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleFloats(self):
        field = FieldContainer(100*copy.deepcopy(self.testData).astype('f'),
                               '10 muA',longname=self.longname,
                               shortname=self.shortname,rescale=True)
        nt.assert_array_almost_equal(self.testData,field.data,5,'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),'mA','Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleFloatsMeter(self):
        field = FieldContainer(100*copy.deepcopy(self.testData).astype('f'),
                               '1 cm**2/mm',longname=self.longname,
                               shortname=self.shortname,rescale=True)
        nt.assert_array_almost_equal(10*self.testData,field.data,5,'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),'m','Wrong baseunit: %s.' % field.unit.unit.name())

    def testRescaleBaseUnitsInteger(self):
        field = FieldContainer(copy.deepcopy(self.testData),
                               '1 cm**2/mm',longname=self.longname,
                               shortname=self.shortname,rescale=True)
        nt.assert_array_equal(self.testData,field.data,'Wrong scaling of field.')
        self.assertEqual(field.unit.unit.name(),'dm','Wrong baseunit: %s.' % field.unit.unit.name())

    def testUnitInteger(self):
        field = FieldContainer(copy.deepcopy(self.testData),
                               unit=self.unit,longname=self.longname,
                               shortname=self.shortname,rescale=True)
        self.assertEqual(field.unit,self.unit,"An integer field should not be rescaled, but should hold the normation constant in its unit.")

    def testDimensionsRescaling(self):
        """Option rescale=True should also rescale the dimensions of the FieldContainer."""
        dim = [FieldContainer(1000*scipy.linspace(0,1,3),unit='1 nm',longname="Axis %s" % axis,shortname=axis) for axis in ['x','y']]
        field = FieldContainer(copy.deepcopy(self.testData),dimensions=dim,
                               unit=self.unit,longname=self.longname,
                               shortname=self.shortname,rescale=True)
        for dim in [0,1]:
            axisUnit   = field.dimensions[dim].unit
            self.assertEqual(axisUnit.unit.name(),'mum')

class FieldContainerSlicing1d(unittest.TestCase):
    def setUp(self):
        self.field1d = FieldContainer(numpy.linspace(0.1,1,10), longname="voltage", 
                                      shortname="U", unit="1V")
    def testSingleIndex(self):
        section = self.field1d[0]
        afoot = FieldContainer(numpy.array([0.1]), longname="afoot", 
                               shortname="U", unit="1V", dimensions=[],
                               attributes={u'Index':(u'i',0)})
        assertEqual(section,afoot)

    def testRegionIndex(self):
        section = self.field1d[1:4]
        afoot = FieldContainer(numpy.linspace(0.2,0.4,3), longname="voltage", 
                                      shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1,3,3)
        self.assertEqual(section,afoot)
        section = self.field1d[1:-1]
        afoot = FieldContainer(numpy.linspace(0.2,0.9,8), longname="voltage", 
                                      shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1,8,8)
        self.assertEqual(section,afoot)

    def testCommaSeparated(self):
        section = self.field1d[[1,3,7],]
        afoot = FieldContainer(numpy.array([0.2,0.4,0.8]), longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.array([1,3,7])
        self.assertEqual(section,afoot)
        section = self.field1d[[[1,3,7]]]
        self.assertEqual(section,afoot)

    def testRegionIndexUnit(self):
        f = self.field1d.dimensions[0]
        mask = slice(3, 7)
        afoot = FieldContainer(self.field1d.data[mask],
                               dimensions=[f[mask]],
                               longname="voltage",
                               shortname="U",
                               unit="1V")
        self.assertRaises(NotImplementedError, self.field1d.__getitem__, "0.4:0.6")
        section = self.field1d["3:7"]
        assertEqual(section, afoot)


class FieldContainerSlicing1dDim(FieldContainerSlicing1d):
    def setUp(self):
        super(FieldContainerSlicing1dDim, self).setUp()
        self.xDim = FieldContainer(numpy.linspace(0.3,0.7,self.field1d.data.shape[0]), longname="current",
                                   shortname="I", unit="1A")
        self.field1d.dimensions[0] = self.xDim

    def testSingleIndex(self):
        section = self.field1d[0]
        afoot = FieldContainer(numpy.array([0.1]), longname="afoot", 
                               shortname="U", unit="1V", dimensions=[self.xDim[0]],
                               attributes={u'current':(u'I',PhysicalQuantity("0.3A"))})
        assertEqual(section,afoot)

    def testRegionIndex(self):
        section = self.field1d[1:4]
        afoot = FieldContainer(numpy.linspace(0.2,0.4,3), longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.xDim[1:4]
        self.assertEqual(section,afoot)
        section = self.field1d[1:-1]
        afoot = FieldContainer(numpy.linspace(0.2,0.9,8), longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.xDim[1:-1]
        self.assertEqual(section,afoot)

    def testCompleteRightOpenIntervall(self):
        dim = self.xDim
        intStart = dim.data.min()*dim.unit
        intEnd   = dim.data.max()*dim.unit
        unitname = dim.unit.unit.name()
        section = self.field1d["%.4f%s:%.4f%s"%(intStart.value,unitname,intEnd.value,unitname)]
        afoot = FieldContainer(numpy.linspace(0.1,0.9,9), longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.xDim[0:-1]
        self.assertEqual(section,afoot)

    def testCompleteIntervall(self):
        dim = self.xDim
        intStart = dim.data.min()*dim.unit
        intEnd   = dim.data.max()*dim.unit*1.001
        unitname = dim.unit.unit.name()
        argument = "%.4f%s:%.4f%s"%(intStart.value,unitname,intEnd.value,unitname)
        section = self.field1d[argument]
        self.assertEqual(section,self.field1d)

    def testCommaSeparated(self):
        section = self.field1d[[1,3,7],]
        afoot = FieldContainer(numpy.array([0.2,0.4,0.8]), longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.xDim[[1,3,7],]
        self.assertEqual(section,afoot)
        section = self.field1d[[[1,3,7]]]
        self.assertEqual(section,afoot)

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
        l = numpy.linspace(0,0.9,10)
        m = numpy.meshgrid(l, l*10)
        self.field2d = FieldContainer(m[0]+m[1], longname="voltage", 
                                      shortname="U", unit="1V")

    def testSingleIndex(self):
        section = self.field2d[0]
        afoot = FieldContainer(numpy.linspace(0,0.9,10), longname="voltage", 
                               shortname="U", unit="1V",
                               attributes={u'Index':(u'j',0)})
        self.assertTrue(section.isValid())
        self.assertEqual(section,afoot)

    def testRegionIndex(self):
        section = self.field2d[1:4]
        afoot = FieldContainer(self.field2d.data[1:4], longname="afoot", 
                               shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1,3,3)
        self.assertEqual(section,afoot)
        section = self.field2d[1:-1]
        afoot = FieldContainer(self.field2d.data[1:-1], longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.linspace(1,8,8)
        self.assertEqual(section,afoot)

    def testCommaSeparated(self):
        section = self.field2d[[1,3,7],]
        afoot = FieldContainer(self.field2d.data[[1,3,7],], longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0].data = numpy.array([1,3,7])
        self.assertEqual(section,afoot)
        section = self.field2d[[[1,3,7]]]
        self.assertEqual(section,afoot)


class FieldContainerSlicing2dDim(FieldContainerSlicing2d):
    def setUp(self):
        super(FieldContainerSlicing2dDim, self).setUp()
        self.xDim = FieldContainer(numpy.linspace(0.3,0.7,self.field2d.data.shape[0]), longname="current",
                                   shortname="I", unit="1A")
        self.yDim = FieldContainer(numpy.linspace(30,70,self.field2d.data.shape[0]), longname="position",
                                   shortname="p", unit="1cm")
        self.field2d.dimensions = [self.yDim,self.xDim]

    def testSingleIndex(self):
        section = self.field2d[0]
        afoot = FieldContainer(numpy.linspace(0,0.9,10), longname="voltage", 
                               shortname="U", unit="1V",
                               attributes={u'position':(u'p',PhysicalQuantity("30cm"))},
                               dimensions=[self.xDim]) 
        self.assertTrue(section.isValid())
        self.assertEqual(section,afoot)

    def testRegionIndex(self):
        section = self.field2d[1:4]
        afoot = FieldContainer(self.field2d.data[1:4], longname="afoot", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim[1:4]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section,afoot)
        section = self.field2d[1:-1]
        afoot = FieldContainer(self.field2d.data[1:-1], longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim[1:-1]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section,afoot)

    def testCommaSeparated(self):
        section = self.field2d[[1,3,7],]
        afoot = FieldContainer(self.field2d.data[[1,3,7],], longname="voltage", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim[[1,3,7],]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section,afoot)
        section = self.field2d[[[1,3,7]]]
        self.assertEqual(section,afoot)

    def testRegionIndexUnit(self):
        section = self.field2d["4:6dm"]
        afoot = FieldContainer(self.field2d.data[3:7], longname="afoot", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim[3:7]
        afoot.dimensions[1] = self.xDim
        self.assertEqual(section,afoot)

    def testRegionIndexWrongUnit(self):
        self.assertRaises(TypeError, self.field2d.__getitem__, "4:6A")

    def test2FoldRegionIndexUnit(self):
        section = self.field2d["4:6dm","4e-1:.6A"]
        afoot = FieldContainer(self.field2d.data[3:7,3:7], longname="afoot", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim[3:7]
        afoot.dimensions[1] = self.xDim[3:7]
        self.assertEqual(section,afoot)

    def test2ndAxisRegionIndexUnit(self):
        section = self.field2d[:,"4e-1:.6A"]
        afoot = FieldContainer(self.field2d.data[:,3:7], longname="afoot", 
                               shortname="U", unit="1V")
        afoot.dimensions[0] = self.yDim
        afoot.dimensions[1] = self.xDim[3:7]
        self.assertEqual(section,afoot)


if __name__ == "__main__":
    #suite = unittest.TestLoader().loadTestsFromTestCase(IsValidFieldContainer)
    #unittest.TextTestRunner().run(suite)
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FieldContainerSlicing1dDim))
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)


