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
from Scientific.Physics.PhysicalQuantities import (isPhysicalQuantity, PhysicalQuantity,_prefixes)

PREFIXES_METER = copy.deepcopy(_prefixes)
map(lambda r: PREFIXES_METER.remove(r),[('h',  1.e2),('da', 1.e1)])
PREFIXES_METER.append(('',1.0))
PREFIXES = copy.deepcopy(PREFIXES_METER)
map(lambda r: PREFIXES.remove(r),[('d',  1.e-1),('c',  1.e-2)])

import logging
_logger = logging.getLogger("pyphant")

#Default variables of indices
INDEX_NAMES=[u'i', u'j', u'k', u'l', u'm', u'n']

#Default string encoding
enc=lambda s: unicode(s, "utf-8")

#Set USER variable used for the emd5 tag
pltform=platform.system()
if pltform=='Linux':
    USER=enc(os.environ['LOGNAME'])
elif pltform=='Windows':
    try:
        USER=enc(os.environ['USERNAME'])
    except:
        USER=u"Unidentified User"


class IndexMarker(object):
    hash=md5.new().hexdigest()
    shortname=u"i"
    longname=u"index"
    def seal(self, id=None):
        pass

    def __eq__(self,other):
        if type(self) == type(other):
            return True
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)
    
    def isValid(self):
        return True


#INDEX must be a list of objects providing a .seal(self) method.
#It is used as a marker to terminate the recursive inclusion of FieldContainers.
INDEX=[IndexMarker()]

def generateIndex(i, n,indexNames = INDEX_NAMES):
    u"""Returns a FieldContainer for index variables.
    It stores an index vector (0,...,n-1)^T, whose short name
    will be given by the i. element of list indexNames, if i<=n,
    and 'i_\%i' %i otherwise.
    """
    if i<len(indexNames):
        name=u"%s" % indexNames[i]
    else:
        name=u"i_%i"%i
    return FieldContainer(scipy.arange(0,n), dimensions=INDEX,
                          longname=u"Index", shortname=name)

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

    
def slice2ind(arg, dim):
    if isinstance(arg, type("")):
        sl = [ "0"+a for a in arg.split(':')] #Hack for PhysicalQuantities, which does not recognize .6 as a number.
        unit = dim.unit
        try:
            hi = PhysicalQuantity(sl[1])
            try:
                li = PhysicalQuantity(sl[0])
            except:
                li = PhysicalQuantity(float(sl[0]),hi.unit)
            try:
                li, hi = [ i.inUnitsOf(unit.unit).value/unit.value for i in [li,hi] ]
            except TypeError:
                raise TypeError("IncompatibleUnits: Dimension %s: %s [%s] can not be sliced with \"%s\"." 
                                % (dim.longname, dim.shortname, dim.unit, arg))
        except SyntaxError:
            li, hi = [ float(i)/unit for i in sl ]
        f = dim.data
        intervallElements = numpy.logical_and(f>=li, f<hi)
        if numpy.alltrue(intervallElements):
            start = 0
            end   = len(intervallElements)+1
        else:
            dma = numpy.diff(intervallElements).nonzero()
            if len(dma[0])==0:
                raise NotImplementedError("This slice needs interpolation, which is not implemented yet.")
            if li <= f.min():
                start = 0
                end = dma[0][0]+1
            elif hi >= f.max():
                start = dma[0][0]+1
                end = -1
            else:
                start, end = dma[0]+1
        return slice(start, end)
    elif isinstance(arg, type(2)):
        return slice(arg, arg+1)
    else:
        return arg

class FieldContainer(DataContainer):
    u"""FieldContainer(data, unit=1, error=None,dimensions=None, longname=u"Sampled Field",
\t\t\t  shortname=u"\\Psi",rescale=False)
\t  Class describing sampled fields:
\t  .data\t\t- Numpy.array representing the sampled field. 
\t  .unit\t\t- PhysicalQuantity object denoting the unit of the sampled field.
\t  .dimensions\t- List of FieldContainer instances
\t\t\t  describing the dimensions of the sampled field.
\t  .data \t- Sampled field stored as numpy.array, which is rescaled to reasonable basic units if option rescale is chosen.
\t  .error\t- Absolut error of the sampled field stored as numpy.array
\t  .longname \t- Notation of the data, e.g. 'electric field',
\t\t\t  which is used for the automatic annotation of charts.
\t  .shortname \t- Symbol of the physical variable in LaTeX notation, e.g. 'E_\\alpha',
\t\t\t  which is also used for the automatic annotation of charts.
\t  .id \t\t- Identifier of Enhanced MD5 (emd5) format
\t\t\t\temd5://NODE/USER/DATETIME/MD5-HASH.TYPESTRING
\t\t\t  which is set by calling method .seal() and
\t\t\t  indicates that the stored information are unchangable.
\t  .label\t- Typical axis description composed from the meta information of the DataContainer.
Concerning the ordering of data matrices and the dimension list consult http://wiki.pyphant.org/xwiki/bin/view/Main/Dimension+Handling+in+Pyphant.
"""
    typeString = u"field"
    def __init__(self, data, unit=1, error=None, mask=None,
                 dimensions=None, longname=u"Sampled Field",
                 shortname=u"\\Psi", attributes=None, rescale=False):
        DataContainer.__init__(self, longname, shortname, attributes)
        self.data = data
        self.mask = mask
        try:
            self.unit = PhysicalQuantity(unit)
        except:
            try:
                self.unit = PhysicalQuantity("1"+unit)
            except:
                self.unit = unit
        self.error = error
        if dimensions != None:
            self.dimensions = dimensions
        else:
            self.dimensions = [generateIndex(i,n) for i,n in enumerate(data.shape)]
        if rescale:
            self.rescale()
            for dim in self.dimensions:
                dim.rescale()
        assert self.isValid()

    def _getLabel(self):
        if len(self.dimensions)>0:
            dependency = '(%s)' % ','.join( [dim.shortname for dim in self.dimensions] )
        else:
            dependency = ''
        label = u"%s $%s%s$ / %s" % (self.longname.title(), self.shortname, dependency, self.unit)
        try:
            if not isPhysicalQuantity(self.unit) and self.unit == 1:
                label = u"%s $%s%s$ / a.u." % (self.longname.title(),self.shortname,dependency)
        except:
            pass #just a ScientificPython bug
        return label.replace('mu',u'\\textmu{}').replace('1.0 ',r'')
    label=property(_getLabel)

    def _getShortLabel(self):
        if not isPhysicalQuantity(self.unit) and self.unit == 1:
            if self.longname == 'index':
                label = u"%s $%s$" % (self.longname.title(),self.shortname)
            else:
                label = u"%s $%s$ / a.u." % (self.longname.title(),self.shortname)
        else:
            label =  u"%s $%s$ / %s" % (self.longname.title(), self.shortname, self.unit)
        return label.replace('mu',u'\\textmu{}').replace('1.0 ',r'')
    shortlabel=property(_getShortLabel)

    def __deepcopy__(self, memo):
        self.lock.acquire()
        data=copy.deepcopy(self.data, memo)
        data.setflags(write=True)
        mask=copy.deepcopy(self.mask, memo)
        if mask!=None:
            mask.setflags(write=True)
        error=copy.deepcopy(self.error, memo)
        if error!=None:
            error.setflags(write=True)
        dimensions=copy.deepcopy(self.dimensions, memo)
        res = FieldContainer(data, self.unit, error, mask, dimensions,
                             self.longname, self.shortname)
        self.lock.release()
        return res

    def generateHash(self):
        m = md5.new()
        m.update(str(self.data.tolist()))
        m.update(str(self.unit))
        if self.error!=None:
            m.update(str(self.error.tolist()))
        if self.mask!=None:
            m.update(str(self.mask.tolist()))
        m.update(str(self.attributes))
        m.update(self.longname.encode('utf-8'))
        m.update(self.shortname.encode('utf-8'))
        [m.update(dim.hash) for dim in self.dimensions]
        return enc(m.hexdigest())

    def seal(self, id=None):
        self.lock.acquire()
        self.data.setflags(write=False)
        if self.mask!=None:
            self.mask.setflags(write=False)
        if self.error!=None:
            self.error.setflags(write=False)
        if not id:
            for dim in self.dimensions:
                dim.seal()
        super(FieldContainer, self).seal(id)
        self.lock.release()

    def inUnitsOf(self, other):
        if not isPhysicalQuantity(self.unit):
            if isPhysicalQuantity(other.unit):
                raise ValueError("Incompatible Units: self.unit = <%s>, other.unit = <%s>"%(self.unit, other.unit))
            factor = float(self.unit)/float(other.unit)
        elif not isPhysicalQuantity(other.unit):
            raise ValueError("Incompatible Units: self.unit = <%s>, other.unit = <%s>"%(self.unit, other.unit))
        else:
            if not self.unit.isCompatible(other.unit.unit):
                raise ValueError("Incompatible Units: self.unit = <%s>, other.unit = <%s>"%(self.unit, other.unit))
            factor = self.unit.inUnitsOf(other.unit.unit).value/other.unit.value
        newSelf = copy.deepcopy(self)
        newSelf.data *= factor
        if newSelf.error != None:
            newSelf.error *= factor
        newSelf.unit = copy.deepcopy(other.unit)
        return newSelf


    def rescale(self):
        if isPhysicalQuantity(self.unit):
            oldUnit = self.unit.inBaseUnits()
        else:
            return
        #Compute decade of field and multiply it to oldUnit
        oldFieldAmplitude = max(abs(numpy.amax(self.data)),abs(numpy.amin(self.data)))
        oldUnit *= oldFieldAmplitude
        #Compute next lower decade
        decade = scipy.log10(oldUnit.value)
        newDecade = 10**(scipy.floor(decade))
        #Find appropriate prefix
        baseUnit=oldUnit.unit.name()
        if baseUnit == 'm':
            prefixes = PREFIXES_METER
        else:
            prefixes = PREFIXES
        prefixCandidates = map(lambda i: (i[0],abs(i[1]-newDecade)),prefixes)
        optPrefix = min([prefix[1] for prefix in prefixCandidates])
        newPrefix = filter(lambda prefix: prefix[1]==optPrefix,prefixCandidates)[0][0]
        newUnitName = newPrefix+baseUnit
        #Convert to new unit
        newUnit = oldUnit.inUnitsOf(newUnitName)
        unitAmplitude = newUnit.value
        if self.data.dtype.name.startswith('int'):
            self.unit = newUnit/oldFieldAmplitude
            return
        self.data *= unitAmplitude/oldFieldAmplitude
        self.unit = newUnit/unitAmplitude

    def __eq__(self, other):
        if type(self) != type(other):
            _logger.debug('Cannot compare objects with different type (%s and %s).' % (type(self),type(other)))
            return False
        if not (self.typeString == other.typeString):
            _logger.debug('The typeString is not identical.')
            return False
        if (self.mask==None) and (other.mask!=None):
            _logger.debug('The mask of the first field container has not been set, while the mask of the second field container is set to %s.' % other.mask)
            return False
        elif  self.mask!=None and (other.mask==None):
            _logger.debug('The mask of the second field container has not been set, while the mask of the first field container is set to %s.' % self.mask)
            return False
        if not (numpy.alltrue(self.mask==other.mask)):
            _logger.debug('The masks are not identical: %s\n%s' % (self.mask,other.mask))
            return False
        if self.mask!=None:
            data = self.data[numpy.logical_not(self.mask)]
            otherData = other.data[numpy.logical_not(other.mask)]
            if self.error!=None:
                error = self.error[numpy.logical_not(self.mask)]
            else:
                error = self.error
            if other.error!=None:
                otherError = other.error[numpy.logical_not(other.mask)]
            else:
                otherError = other.error
        else:
            data = self.data
            error = self.error
            otherData = other.data
            otherError = other.error
        if (isPhysicalQuantity(self.unit) or isPhysicalQuantity(other.unit)):
            try:
                if not (self.unit.inBaseUnits().unit == other.unit.inBaseUnits().unit):
                    _logger.debug('The units are different.')
                    return False
            except AttributeError:
                _logger.debug('Cannot compare unit with normed quantity: %s, %s' % (self.unit,other.unit))
                return False
            try:
                scaledData = data*self.unit.value
                scaledOtherData = otherData*other.unit.inUnitsOf(self.unit.unit).value
                if not numpy.allclose(scaledData,scaledOtherData):
                    if numpy.sometrue(numpy.isnan(scaledData)):
                        _logger.debug('The fields cannot be compared, because some elements of the first field are NaN and the mask has not been set.')
                    if numpy.sometrue(numpy.isnan(scaledOtherData)):
                        _logger.debug('The fields cannot be compared, because some elements of the second field are NaN and the mask has not been set.')
                    else:
                        difference = numpy.abs(scaledData-scaledOtherData)
                        _logger.debug('The scaled fields differ, data-otherData: %s\n%s\n%s' % (difference.max(),
                                                                                       scaledData,
                                                                                       scaledOtherData))
                    return False
            except ValueError:
                _logger.debug('Shape mismatch: %s != %s' % (self.data.shape,other.data.shape))
                return False
            if error!=None:
                scaledError = error*self.unit.value
                if otherError!=None:
                    otherScaledError = otherError*other.unit.inUnitsOf(self.unit.unit).value
                else:
                    _logger.debug('The errors differ: The error of the second argument is none, while the error of the first argument is %s.' % error)
                    return False
                if not numpy.allclose(scaledError,otherScaledError):
                    _logger.debug('The errors differ: %s\n%s' % (scaledError,otherScaledError))
                    return False
        else:
            if not data.dtype.char in ['S','U']:
                try:
                    scaledData = data*self.unit
                    scaledOtherData = otherData*other.unit
                    if not numpy.allclose(scaledData,scaledOtherData):
                        _logger.debug('The scaled fields differ: %s\n%s'%(scaledData,scaledOtherData))
                        return False
                except ValueError:
                    _logger.debug('Shape mismatch: %s != %s' % (self.data.shape,other.data.shape))
                    return False
                if error==None:
                    if not (otherError==None):
                        _logger.debug('The errors differ: Error of first argument is None, but the error of the second argument is not None.')
                        return False
                else:
                    scaledError = error*self.unit
                    otherScaledError = otherError*other.unit
                    if not numpy.allclose(scaledError,
                                          otherScaledError):
                        _logger.debug('The errors differ: %s\n%s' % (scaledError,otherScaledError))
                        return False
        if not self.attributes == other.attributes:
            _logger.debug('The attribute dictionary differs.')
            return False
        for dimSelf,dimOther in zip(self.dimensions,other.dimensions):
            if dimSelf != dimOther:
                _logger.debug('Different dimensions: %s, %s' % (dimSelf,dimOther))
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, FieldContainer):
            if self.error!=None or other.error!=None:
                return NotImplemented
            else:
                error = None
            if len(self.dimensions) != len(other.dimensions):
                return NotImplemented
            for i in xrange(len(self.dimensions)):
                if not self.dimensions[i] == other.dimensions[i]:
                    return NotImplemented
            if isPhysicalQuantity(self.unit):
                if not isPhysicalQuantity(other.unit):
                    return NotImplemented
                if not self.unit.isCompatible(other.unit.unit):
                    return NotImplemented
                if self.unit >= other.unit:
                    data = self.data+(other.data*other.unit.value*other.unit.unit.conversionFactorTo(self.unit.unit))/self.unit.value
                    unit = self.unit
                else:
                    data = other.data+(self.data*self.unit.value*self.unit.unit.conversionFactorTo(other.unit.unit))/other.unit.value
                    unit = other.unit
            elif isPhysicalQuantity(other.unit):
                return NotImplemented
            else:
                data = (self.data*self.unit) + (other.data*other.unit)
                unit = 1.0
            if self.mask==None:
                mask=other.mask
            elif other.mask==None:
                mask=self.mask
            else:
                mask=self.mask+other.mask
            longname = u"Sum of %s and %s." % (self.longname, other.longname)
            shortname = u"%s + %s" % (self.shortname, other.shortname)
            return FieldContainer(data, unit, error, mask,
                                  copy.deepcopy(self.dimensions),
                                  longname, shortname)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, FieldContainer):
            if self.error!=None or other.error!=None:
                return NotImplemented
            else:
                error = None
            if len(self.dimensions) != len(other.dimensions):
                return NotImplemented
            for i in xrange(len(self.dimensions)):
                if not self.dimensions[i] == other.dimensions[i]:
                    return NotImplemented
            if isPhysicalQuantity(self.unit):
                if not self.unit.isCompatible(other.unit.unit):
                    return NotImplemented
                if self.unit >= other.unit:
                    data = self.data - (other.data*other.unit.value*other.unit.unit.conversionFactorTo(self.unit.unit))/self.unit.value
                    unit = self.unit
                else:
                    data = ((self.data*self.unit.value*self.unit.unit.conversionFactorTo(other.unit.unit))/other.unit.value) - other.data
                    unit = other.unit
            else:
                if isPhysicalQuantity(other.unit):
                    return NotImplemented
                data = (self.data*self.unit) - (other.data*other.unit)
                unit = 1.0
            if self.mask==None:
                mask=other.mask
            elif other.mask==None:
                mask=self.mask
            else:
                mask=self.mask+other.mask
            longname = u"Difference of %s and %s." % (self.longname, other.longname)
            shortname = u"%s - %s" % (self.shortname, other.shortname)
            return FieldContainer(data, unit, error, mask,
                                  copy.deepcopy(self.dimensions),
                                  longname, shortname)
        return NotImplemented

    def __str__(self):
        deps = [ dim for dim in self.dimensions if type(dim)!=type(IndexMarker()) ]
        report  = "\nFieldContainer %s of shape %s with field\n%s\n"% (self.label,self.data.shape,self.data)
        if self.error != None:
            report += ", error\n%s\n" % self.error
        if self.mask !=None:
            report += ", mask\n%s\n" % self.mask
        if len(deps)>0:
            report += 'depending on dimensions %s\n' % deps
        if len(self.attributes)>0:
            report += 'and attributes\n%s\n' % self.attributes
        return report

    def __repr__(self):
        return self.__str__()
    
    def __getitem__(self, args):
        if isinstance(args, type("")):
            args=[args]
        try:
            len(args)
        except:
            args = [args]
        args = [ slice2ind(arg, self.dimensions[dim]) for dim, arg in enumerate(args) ]
        data = self.data[args]
        attributes = copy.deepcopy(self.attributes)
        mask = None
        error = None
        dimensions = []
        for i,l in enumerate(data.shape[:len(args)]):
            dim = self.dimensions[i]
            if l==1:
                attributes[dim.longname] = (dim.shortname, dim.data[args[i]].squeeze()*dim.unit)
            else:
                if isinstance(dim, IndexMarker):
                    dimensions.append(dim)
                else:
                    dimensions.append(dim[args[i],])
        for i in xrange(len(args),len(data.shape)):
            dimensions.append(copy.deepcopy(self.dimensions[i]))
        if data.shape != (1,):
            data = data.squeeze()
            if self.mask!=None:
                mask = self.mask[args].squeeze()
            if self.error!=None:
                error = self.error[args].squeeze()
        else:
            if self.mask!=None:
                mask = self.mask[args]
            if self.error!=None:
                error = self.error[args]
        field = FieldContainer(data, dimensions=dimensions,
                               longname=self.longname,
                               shortname=self.shortname,
                               mask=mask,
                               error=error,
                               unit=self.unit,
                               attributes=attributes)
        return field

    def isValid(self):
        if (not (len(self.dimensions)==1 
                 and isinstance(self.dimensions[0], IndexMarker))
            and not (self.data.shape == (1,) and len(self.dimensions)==0)):
            dimshape = tuple([len(d.data) for d in self.dimensions])
            if self.data.shape!=dimshape:
                _logger.debug("Shape of data %s and of dimensions %s do not match for field\n:%s" % 
                              (self.data.shape, dimshape, self))
                return False
            for d in self.dimensions:
                if not d.isValid():
                    _logger.debug("Invalid dimension %s."%d.longname)
                    return False
        if (self.mask!=None) and (self.data.shape!=self.mask.shape):
            _logger.debug("Shape of data %s and of mask %s do not match."%(self.data.shape, self.mask.shape))
            return False
        if (self.error!=None) and (self.data.shape!=self.error.shape):
            _logger.debug("Shape of data %s and of error %s do not match."%(self.data.shape, self.error.shape))
            return False
        return True

    maskedData = property( lambda self: numpy.ma.array(self.data, mask=self.mask) )
    maskedError = property( lambda self: numpy.ma.array(self.error, mask=self.mask) )


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

def assertEqual(con1,con2):
    diagnosis=StringIO.StringIO()
    testReport = logging.StreamHandler(diagnosis)
    logger = logging.getLogger("pyphant")
    logger.addHandler(testReport)
    logger.setLevel(logging.DEBUG)
    if con1 == con2:
        return True
    else:
        raise AssertionError, diagnosis.getvalue()

