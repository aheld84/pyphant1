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
\t  .units \t- List of Quantities objects denoting the units of
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

    def _getCommands(self, expression):
        """
        This method generates nested tuples of filter commands to be applied
        to a SampleContainer out of a string expression. For details of the
        output see SampleContainer.filter()
        expression -- String describing the filter commands. For details
                      see SampleContainer.filter(expression)
        """
        #TODO: compare SCColumns with each other,
        #      allow multi dimensional columns (think up new syntax)
        import re
        #test for expressions containing whitespaces only:
        if len(re.findall(r'\S', expression)) == 0:
            return ()
        #prepare regular expressions
        reDoubleQuotes = re.compile(r'("[^"][^"]*")')
        reSplit = re.compile(
            r'(<(?!=)|<=|>(?!=)|>=|==|!=|not|NOT|and|AND|or|OR|\(|\))'
            )
        reCompareOp = re.compile(r'<|>|==|!=')
        #split the expression
        DQList = reDoubleQuotes.split(expression)
        splitlist = []
        for dq in DQList:
            if reDoubleQuotes.match(dq) != None: splitlist.append(dq)
            else: splitlist.extend(reSplit.split(dq))
        #identify splitted Elements
        al = [] #<-- abstractlist containing tuples of (type, expression)
        for e in splitlist:
            if len(re.findall(r'\S', e)) == 0: pass #<-- skip whitespaces
            elif reCompareOp.match(e) != None:
                al.append(('CompareOp', e))
            elif reSplit.match(e) != None:
                al.append(('Delimiter', e.lower()))
            elif reDoubleQuotes.match(e) != None:
                column = None
                try:
                    column = self[e[1:-1]]
                except:
                    raise IndexError(
                        'Could not find column ' + e + ' in "'
                        + self.longname + '".'
                        )
                al.append(('SCColumn', column))
            else:
                try:
                    phq = Quantity(e)
                    al.append(('PhysQuant', phq))
                    continue
                except:
                    try:
                        number = Quantity(e+' m')
                        al.append(('Number', eval(e)))
                        continue
                    except: pass
                    raise ValueError, "Error parsing expression: " + e
        #resolve multiple CompareOps like a <= b <= c == d:
        i = 0
        values = ['PhysQuant', 'SCColumn', 'Number']
        start_sequence = -1
        while i < len(al) - 4:
            if ((al[i][0] in values) and (al[i+1][0] == 'CompareOp')
                and (al[i+2][0] in values) and (al[i+3][0] == 'CompareOp')
                and (al[i+4][0] in values)):
                if start_sequence == -1:
                    start_sequence = i
                al.insert(i+3, ('Delimiter', 'and'))
                al.insert(i+4, al[i+2])
                i += 4
            else:
                #'not' has higher precedence than 'and':
                if start_sequence != -1:
                    al.insert(start_sequence, ('Delimiter', '('))
                    al.insert(i+4, ('Delimiter', ')'))
                    start_sequence = -1
                    i += 3
                else:
                    i += 1
        if start_sequence != -1:
            al.insert(start_sequence, ('Delimiter', '('))
            al.insert(i+4, ('Delimiter', ')'))
        #identify atomar components like "a" <= 10m, 10s > "b",
        #... and compress them:
        if al[0][0] == 'CompareOp':
            raise ValueError(
                al[0][1] + " may not stand at the beginning of an expression!"
                )
        i = 1
        valid = False
        while i < len(al):
            if al[i][0] == 'CompareOp':
                left = al.pop(i-1)
                middle = al.pop(i-1)
                right = al.pop(i-1)
                if left[0] not in values:
                    raise TypeError, str(left[1]) + " is not a proper value."
                if right[0] not in values:
                    raise TypeError, str(right[1]) + " is not a proper value."
                al.insert(i-1, ('Atomar', left, middle[1], right))
                valid = True
            i += 1
        if not valid:
            raise ValueError(
                "There has to be at least one valid comparison: " + expression
                )

        def compressBraces(sublist):
            """
            Identifies braces and compresses them recursively.
            sublist -- list of filter commands
            """
            openbraces = 0
            start = 0
            end = 0
            finished = False
            for i in range(len(sublist)):
                if sublist[i] == ('Delimiter', '('):
                    openbraces += 1
                    if openbraces == 1 and not finished:
                        start = i
                elif sublist[i] == ('Delimiter', ')'):
                    openbraces -= 1
                    if openbraces == 0 and not finished:
                        end = i
                        finished = True
            if openbraces != 0:
                raise ValueError(
                    "There are unmatched braces within the expression: "
                    + expression
                    )
            if start == 0 and end == 0:
                #no more braces found: end of recursion
                return sublist[:]
            else:
                if end-start == 1:
                    raise ValueError(
                        "There are braces enclosing nothing in the expression: "
                        + expression
                        )
                middle = None
                if end-start == 2:
                    #discard unnecessary braces in order to reduce
                    #recursion depth later on:
                    middle = sublist[start+1:start+2]
                else:
                    middle = [('Brace', compressBraces(sublist[start+1:end]))]
                return sublist[0:start]+middle+compressBraces(sublist[end+1:])
        #TODO: The following three methods could be merged into one generalized
        #method for compressing unitary and binary operators. This would be
        #useful in a future version when there are lots of operators to be
        #supported.

        def compressNot(sublist):
            """
            Identifies "not"s and compresses them recursively.
            sublist -- list of filter commands
            """
            i = 0
            while i < len(sublist):
                if sublist[i] == ('Delimiter', 'not'):
                    if i+1 >= len(sublist):
                        raise ValueError(
                            "'not' must not stand at the end of an expression: "
                            + expression
                            )
                    x = sublist[i+1]
                    if x[0] == 'Atomar':
                        retlist = sublist[0:i] + [('NOT', x)]
                        retlist += compressNot(sublist[i+2:])
                        return retlist
                    elif x[0] == 'Brace':
                        retlist = sublist[0:i]
                        retlist += [('NOT', ('Brace', compressNot(x[1])))]
                        retlist += compressNot(sublist[i+2:])
                        return retlist
                    else:
                        raise ValueError(
                            "'not' cannot be applied to " + str(x) + "."
                            )
                elif sublist[i][0] == 'Brace':
                    retlist = sublist[0:i]
                    retlist += [('Brace', compressNot(sublist[i][1]))]
                    retlist += compressNot(sublist[i+1:])
                    return retlist
                i += 1
            return sublist[:]

        def compressAnd(sublist, start=0):
            """
            Identifies "and"s and compresses them recursively:
            start -- start == 1 indicates that the 1st element of sublist
                     has already been compressed. This is necessary for
                     binary operators.
            sublist -- list of filter commands
            """
            i = start
            while i < len(sublist):
                if sublist[i] == ('Delimiter', 'and'):
                    left = None
                    if start == 1 and i == 1: left = sublist[i-1]
                    else: left = compressAnd(sublist[i-1:i])[0]
                    if left[0] not in ['NOT', 'AND', 'Brace', 'Atomar']:
                        raise ValueError(
                            "'and' cannot be applied to " + str(left) + "."
                            )
                    right = compressAnd(sublist[i+1:i+2])[0]
                    if right[0] not in ['NOT', 'AND', 'Brace', 'Atomar']:
                        raise ValueError(
                            "'and' cannot be applied to " + str(right) + "."
                            )
                    retlist = sublist[0:i-1]
                    retlist += compressAnd([('AND', left, right)]+sublist[i+2:],
                                           1)
                    return retlist
                elif sublist[i][0] == 'Brace':
                    retlist = sublist[0:i]
                    retlist += compressAnd([('Brace',
                                             compressAnd(sublist[i][1]))]
                                           + sublist[i+1:], 1)
                    return retlist
                elif sublist[i][0] == 'NOT':
                    retlist = sublist[0:i]
                    retlist += compressAnd([('NOT',
                                             compressAnd([sublist[i][1]])[0])]
                                           + sublist[i+1:], 1)
                    return retlist
                i += 1
            return sublist[:]

        def compressOrDCB(sublist, start=0):
            """
            Identifies "or"s and compresses them recursively.
            Decompresses braces in order to reduce recursion depth later on.
            start -- start == 1 indicates that the 1st element of sublist
                     has already been compressed. This is necessary for
                     binary operators.
            sublist -- list of filter commands
            """
            i = start
            while i < len(sublist):
                if sublist[i] == ('Delimiter', 'or'):
                    left = None
                    if start == 1 and i == 1: left = sublist[i-1]
                    else: left = compressOrDCB(sublist[i-1:i])[0]
                    if left[0] not in ['NOT', 'AND', 'Atomar', 'OR']:
                        raise ValueError(
                            "'or' cannot be applied to " + str(left) + "."
                            )
                    right = compressOrDCB(sublist[i+1:i+2])[0]
                    if right[0] not in ['NOT', 'AND', 'Atomar', 'OR']:
                        raise ValueError(
                            "'or' cannot be applied to " + str(right) + "."
                            )
                    retlist = sublist[0:i-1]
                    retlist += compressOrDCB([('OR', left, right)]
                                             + sublist[i+2:], 1)
                    return retlist
                elif sublist[i][0] == 'Brace':
                    inner = compressOrDCB(sublist[i][1])
                    if len(inner) != 1:
                        raise ValueError(
                            "Expression could not be parsed completely."
                            "(probably missing keyword): " + expression
                            )
                    retlist = sublist[0:i]
                    retlist += compressOrDCB(inner + sublist[i+1:], 1)
                    return retlist
                elif sublist[i][0] == 'NOT':
                    retlist = sublist[0:i]
                    retlist += compressOrDCB(
                        [('NOT', compressOrDCB([sublist[i][1]])[0])]
                        + sublist[i+1:], 1
                        )
                    return retlist
                elif sublist[i][0] == 'AND':
                    retlist = sublist[0:i]
                    retlist += compressOrDCB(
                        [('AND',
                          compressOrDCB([sublist[i][1]])[0],
                          compressOrDCB([sublist[i][2]])[0])]
                        + sublist[i+1:], 1)
                    return retlist
                i += 1
            return sublist[:]
        compressed = compressOrDCB(compressAnd(compressNot(compressBraces(al))))
        if len(compressed) != 1:
            raise ValueError(
                "Expression could not be parsed completely"
                "(probably missing keyword): " + expression
                )
        return compressed[0]

    def filter(self, expression):
        """
        Returns a new SampleContainer with filter commands applied to it.
        expression -- can be either a string expression or nested tuples
                      of commands. In case expression is a string (or unicode),
                      the following syntax holds:
                      Let's define
                      <atomar> := <value> <CompareOp> <value>
                      where <value> is either a SC Column accessed as
                      "longname" or "shortname" (including the double quotes)
                      or a number or a string representing a Quantity
                      (e.g. 300nm). And <CompareOp> can be ==, !=, <, <=, >, >=.
                      Then a valid expression <expression> is:
                      - <atomar>
                      - (<expression>)
                      - not <expression>
                      - <expression> and <expression>
                      - <expression> or <expression>
                      - NOT, AND, OR is equivalent to not, and, or
                      Precedence is as follows:
                      - multiple CompareOps are evaluated:
                        e.g. a <= b < c --> (a <= b and b < c)
                      - <atomar>
                      - braces
                      - not
                      - and
                      - or
                      If expression is a nested tuple, syntax is as follows:
                      <value> is either ('SCColumn', FieldContainer instance)
                      or ('PhysQuant', Quantity instance)
                      or ('Number', int float etc.)
                      <CompareOp> is in ['==', '!=', ...]
                      A valid nested tuple <nt> can be:
                      - ('Atomar', <value>, <CompareOp>, <value>)
                      - ('NOT', <nt>)
                      - ('AND', <nt>, <nt>)
                      - ('OR', <nt>, <nt>)
                      Precedence is obtained from the way the tuples are nested.
        """
        #determine type of expression:
        from types import StringType, UnicodeType, TupleType
        commands = None
        if isinstance(expression, UnicodeType):
            commands = self._getCommands(expression.encode('utf-8'))
        elif isinstance(expression, StringType):
            commands = self._getCommands(expression)
        elif isinstance(expression, TupleType) or expression == None:
            commands = expression
        else:
            raise TypeError(
                "Expression has to be of StringType, UnicodeType,"
                "TupleType or None. Found " + str(type(expression))
                + " instead!"
                )
        #check for empty commands:
        if commands == None or commands == ():
            return copy.deepcopy(self)
        #generate boolean numpymask from commands using fast numpy methods:
        def evaluateAtomar(atomar):
            left = atomar[1]
            if left[0] == 'SCColumn':
                if left[1].data.ndim != 1:
                    raise NotImplementedError(
                        'Comparing columns of dimensions other than one '
                        'is not yet implemented: "' + left[1].longname + '"'
                        )
            right = atomar[3]
            if right[0] == 'SCColumn':
                if right[1].data.ndim != 1:
                    raise NotImplementedError(
                        'Comparing columns of dimensions other than one '
                        'is not yet implemented: "' + right[1].longname + '"'
                        )
            leftvalue = None
            rightvalue = None
            if left[0] == 'SCColumn' and right[0] == 'SCColumn':
                number = right[1].unit/left[1].unit
                if isQuantity(number):
                    raise TypeError(
                        'Cannot compare "' + left[1].longname + '" to "'
                        + right[1].longname + '".'
                        )
                leftvalue = left[1].data
                rightvalue = right[1].data*number
            elif left[0] == 'SCColumn':
                number = right[1]/left[1].unit
                if isQuantity(number):
                    raise TypeError(
                        'Cannot compare "' + left[1].longname
                        + '" to ' + str(right[1]) + '".'
                        )
                leftvalue = left[1].data
                rightvalue = number
            elif right[0] == 'SCColumn':
                number = left[1]/right[1].unit
                if isQuantity(number):
                    raise TypeError(
                        "Cannot compare " + str(left[1]) + ' to "'
                        + right[1].longname + '".'
                        )
                leftvalue = number
                rightvalue = right[1].data
            else:
                raise ValueError(
                    "At least one argument of '" + atomar[2][1]
                    + "' has to be a column."
                    )
            if   atomar[2] == '==': return leftvalue == rightvalue
            elif atomar[2] == '!=': return leftvalue != rightvalue
            elif atomar[2] == '<=': return leftvalue <= rightvalue
            elif atomar[2] == '<' : return leftvalue <  rightvalue
            elif atomar[2] == '>=': return leftvalue >= rightvalue
            elif atomar[2] == '>' : return leftvalue >  rightvalue
            raise ValueError, "Invalid atomar expression: " + str(atomar)

        def getMaskFromCommands(cmds):
            """
            Returns a boolean numpy mask from given commands.
            cmds -- nested tuples of commands (see SampleContainer.filter())
            """
            if cmds[0] == 'Atomar':
                return evaluateAtomar(cmds)
            elif cmds[0] == 'AND':
                left = getMaskFromCommands(cmds[1])
                right = getMaskFromCommands(cmds[2])
                if left.shape != right.shape:
                    raise TypeError(
                        "Cannot apply 'and' to columns of different shape: "
                        + str(left.shape) + ", " + str(right.shape)
                        )
                return numpy.logical_and(left, right)
            elif cmds[0] == 'OR':
                left = getMaskFromCommands(cmds[1])
                right = getMaskFromCommands(cmds[2])
                if left.shape != right.shape:
                    raise TypeError(
                        "Cannot apply 'or' to columns of different shape: "
                        + str(left.shape) + ", " + str(right.shape)
                        )
                return numpy.logical_or(left, right)
            elif cmds[0] == 'NOT':
                return numpy.logical_not(getMaskFromCommands(cmds[1]))
        numpymask = getMaskFromCommands(commands)
        maskedcolumns = []
        for col in self.columns:
            maskedcol = None
            try:
                maskedcol = col.getMaskedFC(numpymask)
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
                                 longname=self.longname,
                                 shortname=self.shortname,
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
