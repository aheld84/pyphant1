# -*- coding: utf-8 -*-
from __future__ import with_statement

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

u"""
DataContainer \t- A Pyphant modul for self-explanatory scientific data
======================================================================
\nA Pyphant DataContainer presents the following attributes:
\t  .longname \t- Notation of the data, e.g. 'electric field',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation, e.g. 'E_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta information of the DataContainer.
\t  .data \t- Data object, e.g. numpy.array

DataContainer \t\t- Base class for self-explanatory scientific data
FieldContainer \t\t- Class describing sampled fields
SampleContainer \t- Class used for storing realizations of random variables
generateIndex() \t- Function returning an indexing FieldContainer instance
parseId()\t\t- Function returning tupple (HASH,TYPESTRING) from given .id attribute.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"

import scipy, copy, md5, threading, numpy, StringIO
import os, platform, datetime, socket, urlparse
from pyphant.quantities.PhysicalQuantities import (isPhysicalQuantity, PhysicalQuantity,_prefixes)


import logging
_logger = logging.getLogger("pyphant")



#Default string encoding
enc=lambda s: unicode(s, "utf-8")

#Set USER variable used for the emd5 tag
pltform=platform.system()
if pltform=='Linux' or pltform=='Darwin':
    USER=enc(os.environ['LOGNAME'])
elif pltform=='Windows':
    try:
        USER=enc(os.environ['USERNAME'])
    except:
        USER=u"Unidentified User"
else:
    raise NotImplementedError, "Unsupported Platform %s" %pltform



def parseId(id):
    u"""Returns tupple (HASH,TYPESTRING) from given .id attribute."""
    resUri = urlparse.urlsplit(id)
    return resUri[2].split('/')[-1].split('.') #(hash, uriType)


class DataContainer(object):
    u"""DataContainer \t- A Pyphant base class for self-explanatory scientific data
\nDataContainer presents the following attributes:
\t  .longname \t- Notation of the data, e.g. 'electric field',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation, e.g. 'E_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta information of the DataContainer.
    """
    id=None
    hash=None
    masterLock=threading.Lock()
    def __init__(self, longname, shortname, attributes=None):
        self.longname = longname
        self.shortname = shortname
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}

    def appendSubscript(self,index,persistent=True):
        pos = self.shortname.find('_')
        if pos == -1:
            subscript = '_{%s}' % index
            result = self.shortname + subscript
        else:
            subscript = '_{%s,%s}' % (self.shortname[pos+1:],index)
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
                super(DataContainer, self).__setattr__("_lock", threading.RLock())
            self.masterLock.release()
            return self._lock
    lock = property(_getLock)

    def __getstate__(self):
        dict=copy.copy(self.__dict__)
        del dict['_lock']
        return dict

    def __setattr__(self, attr, value):
        self.lock.acquire()
        if not self.id:
            super(DataContainer, self).__setattr__(attr, value)
        else:
            raise TypeError("This DataContainer has been sealed and cannot be modified anymore.")
        self.lock.release()

    def seal(self, id=None):
        with self.lock:
            if self.id:
                if id and id != self.id:
                    raise ValueError('Illegal Id "%s" given. Old Id is: "%s".'%(id, self.id))
            elif id:
                self.hash, uriType = parseId(id)
                self.id = id
            else:
                self.hash=self.generateHash()
                self.id=u"emd5://%s/%s/%s/%s.%s" % (enc(socket.getfqdn()),
                                                    USER,
                                                    enc(datetime.datetime.utcnow().isoformat('_')),
                                                    self.hash,
                                                    self.typeString)


from FieldContainer import *


class SampleContainer(DataContainer):
    u"""SampleContainer(columns, longname='Realizations of random variable', shortname='X')
\t  Class of tables storing realizations of random variables as recarray
\t  colums\t: List of FieldContainer instances, each one holding a vector of all
\t\t\t  realizations of one element of the random variable.

\t  .data \t- Table of samples stored in a numpy.ndarray.
\t  .desc \t- Description numpy.dtype of the ndarray.
\t  .units \t- List of PhysicalQuantities objects denoting the units of the columns.
\t  .longname \t- Notation of the data, e.g. 'database query',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation, e.g. 'X_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta information of the DataContainer.
"""
    typeString = u"sample"
    def __init__(self, columns, longname='Realizations of random variable', shortname='X', attributes=None):
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
    columns=property(lambda self:self._columns, _setColumns)

    def _getLabel(self):
        return u"%s %s" % (self.longname,self.shortname)
    label=property(_getLabel)

    def generateHash(self):
        m = md5.new()
        m.update(u''.join([c.hash for c in self.columns]))
        m.update(str(self.attributes))
        m.update(self.longname)
        m.update(self.shortname)
        return enc(m.hexdigest())

    def __deepcopy__(self, memo):
        self.lock.acquire()
        res = SampleContainer.__new__(SampleContainer)
        res.columns=copy.deepcopy(self.columns, memo)
        res.longname=copy.deepcopy(self.longname, memo)
        res.shortname=copy.deepcopy(self.shortname, memo)
        res.attributes=copy.deepcopy(self.attributes, memo)
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

    def __eq__(self,other):
        try:
            if self.longname != other.longname:
                return False
            if self.shortname != other.shortname:
                return False
            if self.attributes != other.attributes:
                return False
            for selfDim,otherDim in zip(self.columns,other.columns):
                if selfDim != otherDim:
                    return False
        except:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def numberOfColumns(self):
        return len(self.columns)

    #helper method for filter(expression) which parses human input to python code, ensuring no harm can be done by eval()
    #this method is discarded
    def _parseExpressionDiscarded(self, expression):
        import re
        reDoubleQuotes = re.compile(r'("[^"][^"]*")')
        reSplit = re.compile(r'(<(?!=)|<=|>(?!=)|>=|==|!=|and|or|not|AND|OR|NOT|\(|\))')
        reCompareOp = re.compile(r'<|>|==|!=')
        
        #split the expression
        DQList = reDoubleQuotes.split(expression)
        splitlist = []
        for dq in DQList:
            if reDoubleQuotes.match(dq) != None: splitlist.append(dq)
            else: splitlist.extend(reSplit.split(dq))

        #identify splitted Elements
        abstractlist = []
        for e in splitlist:
            if len(re.findall(r'\S', e)) == 0: pass
            elif reCompareOp.match(e) != None:
                abstractlist.append(('CompareOp', e))
            elif reSplit.match(e) != None:
                abstractlist.append(('Delimiter', e.lower()))
            elif reDoubleQuotes.match(e) != None:
                try:
                    dummy = self[e[1:-1]]
                except:
                    print('Could not find column ' + e + ' in "' + self.longname + '".')
                    return None
                abstractlist.append(('SCColumn', e))
            else:
                try:
                    phq = PhysicalQuantity(e)
                    abstractlist.append(('PhysQuant', e))
                except:
                    try:
                        number = PhysicalQuantity(e+' m')
                        abstractlist.append(('Number', e))
                        continue
                    except: pass
                    print("Error parsing expression: "+e)
                    return None
        
        #resolve multiple CompareOps like a <= b <= c == d:
        ral = abstractlist[:]    #future resolved abstractlist
        i = 0
        values = ['PhysQuant', 'SCColumn', 'Number']
        while i < len(ral) - 4:
            if (ral[i][0] in values) and (ral[i+1][0] == 'CompareOp') and (ral[i+2][0] in values) and (ral[i+3][0] == 'CompareOp') and (ral[i+4][0] in values):
                ral.insert(i+3, ('Delimiter', 'and'))
                ral.insert(i+4, ral[i+2])
                i += 4
            else: i += 1
            
        #parse splitted expression to fit requierements of python eval() method:
        parsed = ''
        for i in range(len(ral)):
            currtype = ral[i][0]
            currexpr = ral[i][1]
            if currtype == 'PhysQuant': parsed += ' PhysicalQuantity("' + currexpr + '") '
            elif currtype == 'SCColumn': parsed += ' self[' + currexpr + '].data[index]*self[' + currexpr + '].unit '
            else: parsed += ' ' + currexpr + ' '

        return parsed
    

    #returns new SampleContainer containing all entries that match expression
    #this method has been replaced by the new version of SampleContainer.filter
    def filterDiscarded(self, expression):
        if expression == '':
            return copy.deepcopy(self)

        parsed = self._parseExpressionDiscarded(expression)
        if parsed == None:
            return None

        #TODO: check whether all columns have same length

        #create the selection mask
        mask = []
        for index in range(len(self.columns[0].data)):
            boolexpr = False
            try:
                boolexpr = eval(parsed)
            except:
                print('Error evaluating ' + parsed)
                return None
            
            mask.append(boolexpr)
        numpymask = numpy.array(mask)
        
        #apply mask to data, error and dimensions
        maskedcolumns = copy.deepcopy(self.columns)
        for index in range(len(maskedcolumns)):
            if maskedcolumns[index].data != None:
                maskedcolumns[index].data = self.columns[index].data[numpymask]
            if maskedcolumns[index].error != None:
                maskedcolumns[index].error = self.columns[index].error[numpymask]
            if maskedcolumns[index].dimensions != None:
                maskedcolumns[index].dimensions[0].data = self.columns[index].dimensions[0].data[numpymask]

        #build new SampleContainer from masked data and return it
        result = SampleContainer(maskedcolumns,
                                 longname=self.longname,
                                 shortname=self.shortname,
                                 attributes=copy.deepcopy(self.attributes))
        return result


    #This method generates nested tuples of filter commands to be applied to a SampleContainer out of a string expression
    def _getCommands(self, expression):
        #TODO: "or" keyword
        
        import re
        #test for expressions containing whitespaces only:
        if len(re.findall(r'\S', expression)) == 0:
            return None
        
        #prepare regular expressions
        reDoubleQuotes = re.compile(r'("[^"][^"]*")')
        reSplit = re.compile(r'(<(?!=)|<=|>(?!=)|>=|==|!=|not|NOT|and|AND|\(|\))')
        reCompareOp = re.compile(r'<|>|==|!=')
        
        #split the expression
        DQList = reDoubleQuotes.split(expression)
        splitlist = []
        for dq in DQList:
            if reDoubleQuotes.match(dq) != None: splitlist.append(dq)
            else: splitlist.extend(reSplit.split(dq))

        #identify splitted Elements
        al = [] #abstractlist containing tuples of (type, expression)
        for e in splitlist:
            if len(re.findall(r'\S', e)) == 0: pass #skip whitespaces
            elif reCompareOp.match(e) != None:
                al.append(('CompareOp', e))
            elif reSplit.match(e) != None:
                al.append(('Delimiter', e.lower()))
            elif reDoubleQuotes.match(e) != None:
                column = None
                try:
                    column = self[e[1:-1]]
                except:
                    raise IndexError, 'Could not find column ' + e + ' in "' + self.longname + '".'
                if column.data.ndim != 1:
                    raise NotImplementedError, "Comparing columns of dimensions other than one is not yet implemented: " + e
                al.append(('SCColumn', column))
            else:
                try:
                    phq = PhysicalQuantity(e)
                    al.append(('PhysQuant', phq))
                    continue
                except:
                    try:
                        number = PhysicalQuantity(e+' m')
                        al.append(('Number', eval(e)))
                        continue
                    except: pass
                    raise ValueError, "Error parsing expression: " + e
        
        #resolve multiple CompareOps like a <= b <= c == d:
        i = 0
        values = ['PhysQuant', 'SCColumn', 'Number']
        while i < len(al) - 4:
            if (al[i][0] in values) and (al[i+1][0] == 'CompareOp') and (al[i+2][0] in values) and (al[i+3][0] == 'CompareOp') and (al[i+4][0] in values):
                al.insert(i+3, ('Delimiter', 'and'))
                al.insert(i+4, al[i+2])
                i += 4
            else: i += 1

        #identify atomar components like "a" <= 10, 10 > "a", ... and compress them:
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
        if not valid: raise ValueError, "There has to be at least one valid comparison: " + expression
                
        #identify braces and compress them recursively:
        def compressBraces(sublist):
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
                raise ValueError, "There are unmatched braces within the expression: " + expression
            if start==0 and end==0:
                #no more braces found: end of recursion
                return sublist[:]
            else:
                if end-start == 1:
                    raise ValueError, "There are braces enclosing nothing in the expression: " + expression
                middle = None
                if end-start == 2:
                    #discard unnecessary braces:
                    middle = sublist[start+1:start+2]
                else:
                    middle = [('Brace', compressBraces(sublist[start+1:end]))]
                return sublist[0:start] + middle + compressBraces(sublist[end+1:])
        
        #identify "not"s and compress them recursively:
        def compressNot(sublist):
            i = 0
            while i < len(sublist):
                if sublist[i] == ('Delimiter', 'not'):
                    if i+1 >= len(sublist):
                        raise ValueError, "'not' must not stand at the very end of an expression: " + expression
                    x = sublist[i+1]
                    if x[0] == 'Atomar':
                        return sublist[0:i] + [('NOT', x)] + compressNot(sublist[i+2:])
                    elif x[0] == 'Brace':
                        return sublist[0:i] + [('NOT', ('Brace', compressNot(x[1])))] + compressNot(sublist[i+2:])
                    else:
                        raise ValueError, "'not' cannot be applied to " + str(x) + "."
                elif sublist[i][0] == 'Brace':
                    return sublist[0:i] + [('Brace', compressNot(sublist[i][1]))] + compressNot(sublist[i+1:])
                i += 1
            return sublist[:]
                        

        #identify "and"s and compress them recursively:
        def compressAnd(sublist, start=0):
            i = start
            while i < len(sublist):
                if sublist[i] == ('Delimiter', 'and'):
                    left = None
                    if start == 1 and i == 1: left = sublist[i-1]
                    else: left = compressAnd(sublist[i-1:i])[0]
                    if left[0] not in ['NOT', 'AND', 'Brace', 'Atomar']:
                        raise ValueError, "'and' cannot be applied to " + str(left) + "."
                    right = compressAnd(sublist[i+1:i+2])[0]
                    if right[0] not in ['NOT', 'AND', 'Brace', 'Atomar']:
                        raise ValueError, "'and' cannot be applied to " + str(right) + "."
                    return sublist[0:i-1] + compressAnd([('AND', left, right)] + sublist[i+2:], 1)
                elif sublist[i][0] == 'Brace':
                    return sublist[0:i] + compressAnd([('Brace', compressAnd(sublist[i][1]))] + sublist[i+1:], 1)
                elif sublist[i][0] == 'NOT':
                    return sublist[0:i] + compressAnd([('NOT', compressAnd([sublist[i][1]])[0])] + sublist[i+1:], 1)
                i += 1
            return sublist[:]

        compressed = compressAnd(compressNot(compressBraces(al)))
        if len(compressed) != 1:
            raise NotImplementedError, "Expression has not been parsed completely. There has to be a bug within the parser."
        return compressed[0]

  
    #returns a new SampleContainer with filter commands applied to it. Expression can be either a string expression or nested tuples of commands
    def filter(self, expression):
        #determine type of expression:
        from types import StringType, UnicodeType, TupleType
        commands = None
        if isinstance(expression, UnicodeType):
            commands = self._getCommands(expression.encode('utf-8'))
        elif isinstance(expression, StringType):
            commands = self._getCommands(expression)
        elif isinstance(expression, TupleType) or expression==None:
            commands = expression
        else:
            raise TypeError, "Expression has to be of StringType, UnicodeType, TupleType or None. Found " + str(type(expression)) +" instead!"
        
        #check for empty commands:
        if commands == None or commands==():
            return copy.deepcopy(self)
        
        #generate boolean numpymask from commands:
        def evaluateAtomar(expr, linkedto):
            if expr[0] == 'SCColumn':
                if linkedto[0] == 'SCColumn':
                    raise NotImplementedError, "Comparing two columns is not yet implemented: " + expr[1].longname + ", " + linkedto[1].longname
                return expr[1].data
            else:
                if linkedto[0] != 'SCColumn':
                    raise TypeError, "Could not link " + str(expr[1]) + " to a column. Tried to link with " + str(linkedto)
                number = expr[1] / linkedto[1].unit
                if isPhysicalQuantity(number):
                    raise TypeError, "Cannot compare " + str(expr[1]) + " to " + linkedto[1].longname
                return number

        def getMaskFromCommands(cmds):
            if cmds[0] == 'Atomar':
                left = evaluateAtomar(cmds[1], cmds[3])
                right = evaluateAtomar(cmds[3], cmds[1])
                if cmds[2] == '==': return left == right
                elif cmds[2] == '!=': return left != right
                elif cmds[2] == '<=': return left <= right
                elif cmds[2] == '<': return left < right
                elif cmds[2] == '>=': return left >= right
                elif cmds[2] == '>': return left > right
            elif cmds[0] == 'Brace':
                if len(cmds[1]) != 1:
                    raise NotImplementedError, "Expression has not been parsed completely. There has to be a bug within the parser."
                else:
                    return getMaskFromCommands(cmds[1][0])
            elif cmds[0] == 'AND':
                left = getMaskFromCommands(cmds[1])
                right = getMaskFromCommands(cmds[2])
                if left.shape != right.shape:
                    raise TypeError, "Cannot apply 'and' to columns of different shape: " + str(left.shape) + ", " + str(right.shape)
                return numpy.logical_and(left, right)
            elif cmds[0] == 'OR':
                left = getMaskFromCommands(cmds[1])
                right = getMaskFromCommands(cmds[2])
                if left.shape != right.shape:
                    raise TypeError, "Cannot apply 'or' to columns of different shape: " + str(left.shape) + ", " + str(right.shape)
                return numpy.logical_or(left, right)
            elif cmds[0] == 'NOT':
                return numpy.logical_not(getMaskFromCommands(cmds[1]))
                
        numpymask = getMaskFromCommands(commands)
        
        #generate new columns with the boolean mask applied to them
        maskedcolumns = []
        for c in self.columns:
            #mask dimension
            mdims = []
            try:
                for d in c.dimensions:
                    md = copy.deepcopy(d)
                    if mdims == []: #only primary axis has to be masked
                        #mask errors of dimensions
                        if d.error != None:
                            md.error = d.error[numpymask]

                        #mask data of dimensions
                        if d.data != None:
                            md.data = d.data[numpymask]

                    mdims.append(md)
            
                #mask errors:
                cerr = None
                if c.error != None: cerr = c.error[numpymask]
            
                #mask data:
                cdata = None
                if c.data != None: cdata = c.data[numpymask]
            
                maskedcolumns.append(FieldContainer(cdata,
                                                    copy.deepcopy(c.unit),
                                                    cerr,
                                                    copy.deepcopy(c.mask), 
                                                    mdims, 
                                                    longname=c.longname,
                                                    shortname=c.shortname,
                                                    attributes=copy.deepcopy(c.attributes),
                                                    rescale=False))
            except ValueError:
                raise ValueError, 'Column "' + c.longname + '" has not enough rows!'

        #build new SampleContainer from masked columns and return it
        result = SampleContainer(maskedcolumns,
                                 longname=self.longname,
                                 shortname=self.shortname,
                                 attributes=copy.deepcopy(self.attributes))
        return result

    

def assertEqual(con1,con2,rtol=1e-5,atol=1e-8):
    diagnosis=StringIO.StringIO()
    testReport = logging.StreamHandler(diagnosis)
    logger = logging.getLogger("pyphant")
    logger.addHandler(testReport)
    logger.setLevel(logging.DEBUG)
    if con1.__eq__(con2,rtol,atol):
        return True
    else:
        raise AssertionError, diagnosis.getvalue()

