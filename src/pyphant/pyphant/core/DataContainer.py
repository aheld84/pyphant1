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
=============================================================================
**DataContainer** -- A Pyphant module for *self-explanatory scientific data*
=============================================================================

The *DataContainer* is Pypahnt's preferred data exchange class. It is
designed to maximise the interoperability of the various workers
provided by Pyphant.

It can be seen as an interface for exchanging data between workers and
visualizers and among workers. It reproduces the self-descriptiveness of the *network
Common Data Form* (netCDF). Once sealed it is immutable. It can be
identified by its *emd5* attribute, a unique identifier composed of
information about the origin of the container.

There are two kinds of DataContainers:

     - L{FieldContainer}
        - is designed to store *sampled scalar Fields*

     - L{SampleContainer}
        - is designed to store *tabular data*


**SampleConatiner** -- A pyphant module storing tabular data
=============================================================

The *SampleContainer* combines different FieldContainers that have the
same numer of sample points to a table-like representation. It stores
different observations on the same subject per row whereby each column
comprises a quantity of the same kind. Each row can be regarded as the
realization of a random variable.
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
    def _parseExpression(self, expression):
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
    def filter(self, expression):
        parsed = self._parseExpression(expression)
        if parsed == None:
            return None

        #TODO: Nicer Iteration, reject multidim arrays or even better: handle them correctly,
        #      check whether all columns have same length

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

