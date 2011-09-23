# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""
=============================================================================
**DataContainer** -- A Pyphant module for *self-explanatory scientific data*
=============================================================================

The *DataContainer* is Pypahnt's preferred data exchange class. It is
designed to maximize the interoperability of the various workers
provided by Pyphant.

It can be seen as an interface for exchanging data between workers and
visualizers and among workers. It reproduces the self-descriptiveness
of the *network Common Data Form* (netCDF). Once sealed it is
immutable. It can be identified by its *emd5* attribute, a unique
identifier composed of information about the origin of the container.

There are two kinds of DataContainers:

     - L{FieldContainer}
        - is designed to store *sampled scalar Fields*

     - L{SampleContainer}
        - is designed to store *tabular data*


**SampleContainer** -- A pyphant module storing tabular data
=============================================================

The *SampleContainer* combines different FieldContainers that have the
same number of sample points to a table-like representation. It stores
different observations on the same subject per row whereby each column
comprises a quantity of the same kind. Each row can be regarded as the
realization of a random variable.
"""
from __future__ import with_statement

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"

import copy, hashlib, threading, numpy, StringIO
import os, platform, datetime, socket, urlparse
from pyphant.quantities import (isQuantity, Quantity)
import Helpers
from ast import (NodeTransformer, NodeVisitor)
import logging
_logger = logging.getLogger("pyphant")


#Default string encoding
enc = lambda s: unicode(s, "utf-8")

def parseId(id):
    u"""Returns tuple (HASH, TYPESTRING) from given .id attribute."""
    resUri = urlparse.urlsplit(id)
    return resUri[2].split('/')[-1].split('.') #(hash, uriType)


class DataContainer(object):
    u"""DataContainer \t- Base class for self-explanatory scientific data
\nDataContainer presents the following attributes:
\t  .longname \t- Notation of the data, e.g. 'electric field',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation,
\t\t\t  e.g. 'E_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta
\t\t\t  information of the DataContainer.
    """
    id = None
    hash = None
    masterLock = threading.Lock()
    def __init__(self, longname, shortname, attributes=None):
        self.longname = longname
        self.shortname = shortname
        self.machine = Helpers.getMachine()
        self.creator = Helpers.getUsername()
        if type(attributes) == type({}):
            self.attributes = attributes
        else:
            self.attributes = {}

    def appendSubscript(self, index, persistent=True):
        pos = self.shortname.find('_')
        if pos == -1:
            subscript = '_{%s}' % index
            result = self.shortname + subscript
        else:
            subscript = '_{%s,%s}' % (self.shortname[pos+1:], index)
            result = self.shortname[:pos]+subscript
        if persistent:
            self.shortname = result
        return result

    def _getLock(self):
        try:
            return self._lock
        except AttributeError, e:
            self.masterLock.acquire()
            if not hasattr(self, "_lock"):
                super(DataContainer, self).__setattr__("_lock",
                                                       threading.RLock())
            self.masterLock.release()
            return self._lock
    lock = property(_getLock)

    def __getstate__(self):
        dict = copy.copy(self.__dict__)
        del dict['_lock']
        return dict

    def __setattr__(self, attr, value):
        self.lock.acquire()
        if not self.id:
            super(DataContainer, self).__setattr__(attr, value)
        else:
            raise TypeError(
                "This DataContainer has been sealed and cannot"
                "be modified anymore.")
        self.lock.release()

    def generateHash(self, m=None):
        if m == None:
            m = hashlib.md5()
        m.update(self.longname)
        m.update(self.shortname)
        m.update(self.machine)
        m.update(self.creator)
        m.update(str(self.attributes))
        return enc(m.hexdigest())

    def seal(self, id=None):
        with self.lock:
            if self.id:
                if id and id != self.id:
                    raise ValueError('Illegal Id "%s" given. Old Id is: "%s".'
                                     % (id, self.id))
            elif id:
                self.hash, uriType = parseId(id)
                self.id = id
            else:
                self.hash = self.generateHash()
                self.timestamp = datetime.datetime.utcnow()
                self.id = u"emd5://%s/%s/%s/%s.%s" % (self.machine,
                                                      self.creator,
                                                      enc(self.timestamp.isoformat('_')),
                                                      self.hash,
                                                      self.typeString)


from FieldContainer import *


class SampleContainer(DataContainer):
    u"""SampleContainer(columns, longname='Realizations of random variable',
\t\t\t  shortname='X')
\t  Class of tables storing realizations of random variables as recarray
\t  colums\t: List of FieldContainer instances, each one holding a vector of all
\t\t\t  realizations of one element of the random variable.

\t  .data \t- Table of samples stored in a numpy.ndarray.
\t  .desc \t- Description numpy.dtype of the ndarray.
\t  .units \t- List of quantities objects denoting the units of
\t\t\t  the columns.
\t  .longname \t- Notation of the data, e.g. 'database query',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation,
\t\t\t  e.g. 'X_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta information
\t\t\t  of the DataContainer.
"""
    typeString = u"sample"
    def __init__(self, columns, longname='Realizations of random variable',
                 shortname='X', attributes=None):
        """columns: List of FieldContainer"""
        DataContainer.__init__(self, longname, shortname, attributes)
        self._setColumns(columns)

    def _setColumns(self, columns):
        self._columns = columns
        self.longnames = {}
        self.shortnames = {}
        for i in xrange(len(self.columns)):
            self.longnames[self.columns[i].longname] = columns[i]
            self.shortnames[self.columns[i].shortname] = columns[i]
    columns = property(lambda self:self._columns, _setColumns)

    def _getLabel(self):
        return u"%s %s" % (self.longname, self.shortname)
    label = property(_getLabel)

    def _getRawDataBytes(self):
        return [column.rawDataBytes for column in self.columns]
    rawDataBytes = property(_getRawDataBytes)

    def generateHash(self, m=None):
        if m == None:
            m = hashlib.md5()
        super(SampleContainer, self).generateHash(m)
        m.update(u''.join([c.hash for c in self.columns]))
        return enc(m.hexdigest())

    def __deepcopy__(self, memo):
        self.lock.acquire()
        res = SampleContainer.__new__(SampleContainer)
        res.columns = copy.deepcopy(self.columns, memo)
        res.longname = copy.deepcopy(self.longname, memo)
        res.shortname = copy.deepcopy(self.shortname, memo)
        res.creator = copy.deepcopy(self.creator, memo)
        res.machine = copy.deepcopy(self.machine, memo)
        res.attributes = copy.deepcopy(self.attributes, memo)
        self.lock.release()
        return res

    def seal(self, id=None):
        self.lock.acquire()
        [c.seal(c.id) for c in self.columns]
        super(SampleContainer, self).seal(id)
        self.lock.release()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.columns[key]
        try:
            return self.longnames[key]
        except KeyError:
            pass
        try:
            return self.shortnames[key]
        except KeyError:
            pass
        raise KeyError(u'No column named "%s" could be found.'%key)

    def __eq__(self, other):
        try:
            if self.longname != other.longname:
                return False
            if self.shortname != other.shortname:
                return False
            if self.attributes != other.attributes:
                return False
            for selfDim, otherDim in zip(self.columns, other.columns):
                if selfDim != otherDim:
                    return False
        except:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def numberOfColumns(self):
        return len(self.columns)

    def calcColumn(self, exprStr, shortname, longname):
        """
        Return an unsealed FieldContainer generated from `exprStr`.

        Parameters
        ----------
        exprStr : str
            Expression has to be a string. Specifies the mathematical
            operations which will be evaluated to generate a new FieldContainer
            containing the result. `exprStr` may contain FieldContainers,
            PhysicalQuantities, Booleans and Numbers as well as the operators
            listed below.

        shortname : str
            The `shortname` of the returned FieldContainer.

        longname : str
            The `longname`of the returned FieldContainer.

        Syntax
        ------
        FieldContainer
            FieldContainers can be adressed by their `shortname`or `longname`.
            For a FieldContainer with shortname="exampleFC" the syntax within
            `exprStr` is:
                col("exampleFC")
            where `col` stands for column and may be `Col` or `COL` as well.
            Adressing by `longname` works analogously.

        PhysicalQuantity
            Within the expression PhysicalQuantities have to be enquoted:
                "10kg", "100 m", "5 kg * m / s ** 2"
            where the whitespaces are optional.

        Booleans and Numbers
            Can just be used without quotes or braces within `exprStr`:
                True, False, 1.2, 10

        Operators
        ---------
        A list of all implemented operations that can be used within `exprStr`
        sorted by precedence from lowest precedence (least binding) to highest
        precedence (most binding):

        Comparisons: <, <=, >, >=, <>, !=, ==
        Bitwise OR: |
        Bitwise XOR: ^
        Bitwise AND: &
        Addition and Subtraction: +, -
        Multiplication, Division: *, /
        Positive, Negative, Bitwise NOT: +x, -x, ~x

        Not implemented: and, or, not, **, //, %, if - else

        Examples
        --------
        Some examples of valid expressions will be given.
        Data:
            distance = FieldContainer(scipy.array([5., 10., 1.]),
                                    Quantity('1.0 m'),
                                    longname=u"Distance",
                                    shortname=u"s")
            time = FieldContainer(scipy.array([3., 4., 5.]),
                                    Quantity('1.0 s'),
                                    longname=u"Time",
                                    shortname=u"t")
        Examplary expressions:
            exprStr = "col('Distance') / col('Time')"
            exprStr = "col('Distance') - '1 m'"
            exprStr = "col('t') >= '4 s'"
            exprStr = "(col('s') > '1 m') & (COL('Time') == '3s')"

        """
        exprStr = exprStr or 'True'
        import ast
        rpn = ReplaceName(self)
        expr = compile(exprStr, "<calcColumn>", 'eval', ast.PyCF_ONLY_AST)
        replacedExpr = rpn.visit(expr)
        rpo = ReplaceOperator(rpn.localDict)
        factorExpr = rpo.visit(replacedExpr)
        localDict = dict([(key, value.data) \
                          for key, value in rpn.localDict.iteritems()])
        data = eval(compile(factorExpr, '<calcColumn>', 'eval'), {}, localDict)
        unitcalc = UnitCalculator(rpn.localDict)
        unit, dims = unitcalc.getUnitAndDim(replacedExpr)
        if dims is None:
            assert not isinstance(data, numpy.ndarray)
            for col in self.columns:
                checkDimensions(col.dimensions[0],
                                self.columns[0].dimensions[0])
            shape = self.columns[0].dimensions[0].data.shape
            if data:
                data = numpy.ones(shape, dtype=bool)
            else:
                data = numpy.zeros(shape, dtype=bool)
            dims = [self.columns[0].dimensions[0]]
        field = FieldContainer(data, unit, dimensions=dims,
                               longname=longname, shortname=shortname)
        return field

    def filter(self, exprStr, shortname='', longname=''):
        """
        Return an unsealed SampleContainer containing only those rows where
        `exprStr` was evaluated to be True. This method replaces the old
        filter method and is mostly capable of the same operations, yet the
        syntax has changed slightly.

        Parameters
        ----------
        exprStr : str
            A string with a logical expression that has to evaluate to be
            either True or False. This can be for example an inequality or
            a comparison. For all possible operations and a description of
            the syntax as well as examples see `calcColumn`.

        shortname, longname : str, default=''
            Specify the short and long name of the resulting FC.

        """
        shortname = shortname or self.shortname
        longname = longname or self.longname
        mask = self.calcColumn(exprStr, 'm', 'mask')
        assert isinstance(mask.unit, float)
        mask = mask.data
        return self.extractRows(mask, shortname, longname)

    def extractRows(self, mask, shortname, longname):
        """
        Return an unsealed SampleContainer that contains only selected rows. The
        selection is specified via the `mask`.

        Parameters
        ----------
        mask : numpy array of Boolean values
            The length of the array has to be equal to the length of the columns
            of the SampleContainer. If the value of mask[n] is
            True, the nth row is part of the result, else it is discarded.

        shortname, longname : str
            Specify the short and long name of the resulting FC.

        """
        maskedcolumns = []
        for col in self.columns:
            try:
                maskedcol = col.getMaskedFC(mask)
            except ValueError:
                raise ValueError(
                    'Column "' + col.longname + '" has not enough rows!'
                    )
            except AttributeError:
                raise AttributeError(
                    "Masking of SampleContainers as columns is not supported."
                    )
            maskedcolumns.append(maskedcol)
        #build new SampleContainer from masked columns and return it
        result = SampleContainer(maskedcolumns,
                                 longname=longname,
                                 shortname=shortname,
                                 attributes=copy.deepcopy(self.attributes))
        return result


def assertEqual(con1, con2, rtol=1e-5, atol=1e-8):
    diagnosis = StringIO.StringIO()
    testReport = logging.StreamHandler(diagnosis)
    logger = logging.getLogger("pyphant")
    logger.addHandler(testReport)
    logger.setLevel(logging.DEBUG)
    if con1.__eq__(con2, rtol, atol):
        return True
    else:
        raise AssertionError, diagnosis.getvalue()


class LocationFixingNodeTransformer(NodeTransformer):
    def visit(self, *args, **kargs):
        result = NodeTransformer.visit(self, *args, **kargs)
        from ast import fix_missing_locations
        fix_missing_locations(result)
        return result


class ReplaceName(LocationFixingNodeTransformer):
    def __init__(self, sampleContainer):
        self.localDict = {}
        self.count = 0
        self.sc = sampleContainer

    def visit_Call(self, node):
        from ast import (Name, Load)
        if isinstance(node.func, Name) and node.func.id.lower() == 'col':
            newName = self.getName(self.sc[node.args[0].s])
            return Name(newName, Load())

    def visit_Str(self, node):
        from ast import (Name, Load)
        quantity = Quantity(node.s)
        class QuantityDummy(object):
            pass
        dummy = QuantityDummy()
        dummy.unit = Quantity(1.0, quantity.unit)
        dummy.data = quantity.value
        dummy.dimensions = None
        newName = self.getName(dummy)
        return Name(newName, Load())

    def getName(self, ref):
        newName = "N%s" % self.count
        self.count += 1
        self.localDict[newName] = ref
        return newName


class ReplaceOperator(LocationFixingNodeTransformer):
    def __init__(self, localDict):
        self.localDict = localDict

    def visit_BinOp(self, node):
        from ast import (Add, Sub, BinOp)
        self.generic_visit(node)
        unitcalc = UnitCalculator(self.localDict)
        leftUD = unitcalc.getUnitAndDim(node.left)
        rightUD = unitcalc.getUnitAndDim(node.right)
        checkDimensions(leftUD[1], rightUD[1])
        if isinstance(node.op,(Add, Sub)):
            factor = rightUD[0] / leftUD[0]
            right = self.withFactor(factor, node.right)
            binOp = BinOp(node.left, node.op, right)
            return binOp
        else:
            return node

    def visit_Compare(self, node):
        from ast import Compare
        self.generic_visit(node)
        unitcalc = UnitCalculator(self.localDict)
        leftUD = unitcalc.getUnitAndDim(node.left)
        listUD = [unitcalc.getUnitAndDim(comp) for comp in node.comparators]
        nonNoneDims = [ud[1] for ud in listUD + [leftUD] if ud[1] is not None]
        for dims in nonNoneDims:
            checkDimensions(nonNoneDims[0], dims)
        factorlist = [ud[0] / leftUD[0] for ud in listUD]
        newComplist = [self.withFactor(*t) \
                       for t in zip(factorlist, node.comparators)]
        compOp = Compare(node.left, node.ops, newComplist)
        compOpTrans = self.compBreaker(compOp)
        return compOpTrans

    def withFactor(self, factor, node):
        from ast import (BinOp, Num, Mult)
        if not isinstance(factor, float):
            raise ValueError('Incompatible units!')
        if factor == 1.0:
            return node
        return BinOp(Num(factor), Mult(), node)

    def compBreaker(self, node):
        from ast import (Compare, BinOp, BitAnd)
        assert isinstance(node, Compare)
        if len(node.comparators) == 1:
            return node
        else:
            comp1 = Compare(node.left, node.ops[0:1],
                            node.comparators[0:1])
            comp2 = Compare(node.comparators[0],
                            node.ops[1:], node.comparators[1:])
            newNode = BinOp(comp1, BitAnd(), self.compBreaker(comp2))
            return newNode


class UnitCalculator(object):
    def __init__(self, localDict):
        self.localDict = localDict

    def getUnitAndDim(self, node):
        from ast import (Expression, Name, Num,
                         BinOp, Add, Mult, Div, Sub,
                         Compare, BoolOp, UnaryOp,
                         BitOr, BitXor, BitAnd)
        if isinstance(node, Expression):
            return self.getUnitAndDim(node.body)
        elif isinstance(node, Name):
            if node.id in ['True', 'False']:
                return (1.0, None)
            else:
                column = self.localDict[node.id]
                return (column.unit, column.dimensions)
        elif isinstance(node, Num):
            return (1.0, None)
        elif isinstance(node, BinOp):
            left = self.getUnitAndDim(node.left)
            right = self.getUnitAndDim(node.right)
            dimensions = checkDimensions(left[1], right[1])
            if isinstance(node.op, (Add, Sub)):
                if not isinstance(left[0] / right[0], float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left, right))
                unit = left[0]
            elif isinstance(node.op, Mult):
                unit = left[0] * right[0]
            elif isinstance(node.op, Div):
                unit = left[0] / right[0]
            elif isinstance(node.op, (BitOr, BitXor, BitAnd)):
                if not isinstance(left[0], float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % left)
                if not isinstance(right[0], float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % right)
                unit = 1.0
            else:
                raise NotImplementedError()
            return (unit, dimensions)
        elif isinstance(node, Compare):
            left = self.getUnitAndDim(node.left)
            nonNoneDims = []
            if left[1] is not None:
                nonNoneDims.append(left[1])
            for comparator in node.comparators:
                right = self.getUnitAndDim(comparator)
                if right[1] is not None:
                    nonNoneDims.append(right[1])
                if not isinstance(left[0] / right[0], float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left[0], right[0]))
            if len(nonNoneDims) >= 1:
                for dims in nonNoneDims:
                    checkDimensions(nonNoneDims[0], dims)
                dimensions = nonNoneDims[0]
            else:
                dimensions = None
            return (1.0, dimensions)
        elif isinstance(node, BoolOp):
            raise NotImplementedError(
                'BoolOps not supported. Use bitwise ops instead (&, |)!')
        elif isinstance(node, UnaryOp):
            return self.getUnitAndDim(node.operand)
        else:
            raise NotImplementedError()


def checkDimensions(dimensions1, dimensions2):
    if dimensions1 is not None and dimensions2 is not None and \
           dimensions1 != dimensions2:
        msg = 'Dimensions "%s" and "%s" do not match!' \
              % (dimensions1, dimensions2)
        raise ValueError(msg)
    return dimensions1 or dimensions2
