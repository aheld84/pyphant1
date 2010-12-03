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
designed to maximise the interoperability of the various workers
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
same numer of sample points to a table-like representation. It stores
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
from pyphant.quantities import (isQuantity,
                                                   Quantity)
import Helpers
from ast import (NodeTransformer, NodeVisitor)

import logging
_logger = logging.getLogger("pyphant")


#Default string encoding
enc = lambda s: unicode(s, "utf-8")

def parseId(id):
    u"""Returns tupple (HASH, TYPESTRING) from given .id attribute."""
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
        unit = unitcalc.getUnit(replacedExpr)
        field = FieldContainer(data, unit, longname=longname,
                               shortname=shortname)
        field.seal()
        return field

    def filter(self, exprStr, shortname='', longname=''):
        shortname = shortname or self.shortname
        longname = longname or self.longname
        mask = self.calcColumn(exprStr, 'm', 'mask')
        assert isinstance(mask.unit, float)
        mask = mask.data
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


class ReplaceName(NodeTransformer):
    def __init__(self, sampleContainer):
        self.localDict = {}
        self.count = 0
        self.sc = sampleContainer

    def visit_Str(self, node):
        import ast
        self.generic_visit(node)
        return ast.copy_location(ast.Name(self.getName(node.s),
                                          ast.Load()), node)

    def getName(self, oldName):
       newName = "N%s" % self.count
       self.count += 1
       self.localDict[newName] = self.sc[oldName]
       return newName


class ReplaceOperator(NodeTransformer):
    def __init__(self, localDict):
        self.localDict = localDict

    def visit_BinOp(self, node):
        from ast import (Add, Sub, BinOp, copy_location)
        self.generic_visit(node)
        if isinstance(node.op,(Add, Sub)):
            unitcalc = UnitCalculator(self.localDict)
            unitleft = unitcalc.getUnit(node.left)
            unitright = unitcalc.getUnit(node.right)
            factor = unitright / unitleft
            right = self.withFactor(factor, node.right)
            binOp = BinOp(node.left, node.op, right)
            return copy_location(binOp, node)
        else:
            return node

    def visit_Compare(self, node):
        from ast import (Compare, copy_location)
        self.generic_visit(node)
        unitcalc = UnitCalculator(self.localDict)
        unitleft = unitcalc.getUnit(node.left)
        factorlist = [unitcalc.getUnit(comp) / unitleft \
                      for comp in node.comparators]
        newComplist = [self.withFactor(*t) \
                       for t in zip(factorlist, node.comparators)]
        compOp = Compare(node.left, node.ops, newComplist)
        return copy_location(compOp, node)

    def withFactor(self, factor, node):
        from ast import (BinOp, copy_location, Num, Mult)
        if factor == 1.0:
            return node
        return copy_location(BinOp(Num(factor), Mult(), node), node)


class UnitCalculator(object):
    def __init__(self, localDict):
        self.localDict = localDict

    def getUnit(self, node):
        from ast import (Expression, Name, Num,
                         BinOp, Add, Mult, Div, Sub,
                         Compare, BoolOp, UnaryOp,
                         BitOr, BitXor, BitAnd)
        if isinstance(node, Expression):
            return self.getUnit(node.body)
        elif isinstance(node, Name):
            return self.localDict[node.id].unit
        elif isinstance(node, Num):
            return 1.0
        elif isinstance(node, BinOp):
            if isinstance(node.op, (Add, Sub)):
                left = self.getUnit(node.left)
                right = self.getUnit(node.right)
                if not isinstance(left / right, float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left, right))
                return left
            elif isinstance(node.op, Mult):
                return self.getUnit(node.left) * self.getUnit(node.right)
            elif isinstance(node.op, Div):
                return self.getUnit(node.left) / self.getUnit(node.right)
            elif isinstance(node.op, (BitOr, BitXor, BitAnd)):
                left = self.getUnit(node.left)
                right = self.getUnit(node.right)
                if not isinstance(left, float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % left)
                if not isinstance(right, float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % right)
                return 1.0
            else:
                raise NotImplementedError()
        elif isinstance(node, Compare):
            left = self.getUnit(node.left)
            for comparator in node.comparators:
                right = self.getUnit(comparator)
                if not isinstance(left / right, float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left, right))
            return 1.0
        elif isinstance(node, BoolOp):
            raise NotImplementedError(
                'BoolOps not supported. Use bitwise ops instead (&, |)!')
        elif isinstance(node, UnaryOp):
            return self.getUnit(node.operand)
        else:
            raise NotImplementedError()
