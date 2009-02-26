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
=================================================================
The **FieldContainer** -- A module storing sampled scalar fields
=================================================================

The *FieldContainer* represents a class of Pyphant's L{DataContainer}
module.

        That is Pyphant's module for *self-desriptive scientific data*
        which is designed to maximise the interoperability of the various
        workers. It can be seen as an interface for exchanging scientific
        information between workers and visualizers. It reproduces the
        self-descriptiveness of the *network Common Data Form* (netCDF). Once
        sealed a DataContainer is immutable but can be identified by
        its *emd5* format which holds information about the origin of
        the container.

The *FieldContainer* stores a sampled scalar Filed. 

        It holds an *n-dimensional array* together with
        its *unit* and coordinates of the idependent variable (*dimensions*).
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"

import scipy, copy, md5, threading, numpy, StringIO
import os, platform, datetime, socket, urlparse
from pyphant.quantities.PhysicalQuantities import (isPhysicalQuantity, PhysicalQuantity,_prefixes)
from DataContainer import DataContainer, enc, _logger

#Default variables of indices
INDEX_NAMES=[u'i', u'j', u'k', u'l', u'm', u'n']
PREFIXES_METER = copy.deepcopy(_prefixes)
map(lambda r: PREFIXES_METER.remove(r),[('h',  1.e2),('da', 1.e1)])
PREFIXES_METER.append(('',1.0))
PREFIXES = copy.deepcopy(PREFIXES_METER)
map(lambda r: PREFIXES.remove(r),[('d',  1.e-1),('c',  1.e-2)])

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


class DimensionList(list):
    write = True
    def __setitem__(self,i,y):
        if self.write:
            super(DimensionList,self).__setitem__(i,y)
        else:
            raise TypeError, 'Sealed list of dimensions cannot be modified.'

    def __delitem__(self,i):
        if self.write:
            super(DimensionList,self).__delitem__(i,y)
        else:
            raise TypeError, 'Sealed list of dimensions cannot be modified.'

    def seal(self):
        self.write = False

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
            elif hi > f.max():
                start = dma[0][0]+1
                end = len(intervallElements)+1
            elif hi == f.max():
                start = dma[0][0]+1
                end = len(intervallElements)
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
            if isinstance(unit, (str, unicode)):
                unit = unit.replace('^', '**')
            if isinstance(unit, unicode):
                unit = unit.encode('utf-8')
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
            N = len(data.shape)-1
            self.dimensions = [generateIndex(N-i,n) for i,n in enumerate(data.shape)]
        if rescale:
            self.rescale()
            for dim in self._dimensions:
                dim.rescale()
        assert self.isValid()

    def _set_dimensions(self,dimensions):
        self._dimensions = DimensionList(dimensions)

    def _get_dimensions(self):
        return self._dimensions
    dimensions = property(_get_dimensions,_set_dimensions)

    def _getLabel(self):
        if len(self._dimensions)>0:
            shortnames = [dim.shortname for dim in self._dimensions]
            shortnames.reverse()
            dependency = '(%s)' % ','.join(shortnames)
        else:
            dependency = ''
        label = u"%s $%s%s$ / %s" % (self.longname.title(), self.shortname, dependency, self.unit)
        try:
            if not isPhysicalQuantity(self.unit) and self.unit == 1:
                label = u"%s $%s%s$ / a.u." % (self.longname.title(),self.shortname,dependency)
        except:
            pass #just a ScientificPython bug
        return label.replace('1.0 ',r'')#.replace('mu',u'\\textmu{}')
    label=property(_getLabel)

    def _getShortLabel(self):
        if not isPhysicalQuantity(self.unit) and self.unit == 1:
            if self.longname == 'index':
                label = u"%s $%s$" % (self.longname.title(),self.shortname)
            else:
                label = u"%s $%s$ / a.u." % (self.longname.title(),self.shortname)
        else:
            label =  u"%s $%s$ / %s" % (self.longname.title(), self.shortname, self.unit)
        return label.replace('1.0 ',r'')#.replace('mu',u'\\textmu{}')
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
        dimensions=copy.deepcopy(self._dimensions, memo)
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
        [m.update(dim.hash) for dim in self._dimensions]
        return enc(m.hexdigest())

    def seal(self, id=None):
        with self.lock:
            assert self.isValid()
            self.data.setflags(write=False)
            if self.mask!=None:
                self.mask.setflags(write=False)
            if self.error!=None:
                self.error.setflags(write=False)
            if not id:
                self._dimensions.write = False
                for dim in self._dimensions:
                    dim.seal()
            super(FieldContainer, self).seal(id)

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

    def __eq__(self, other, rtol=1e-5, atol=1e-8):
        if type(self) != type(other):
            if type(other) != IndexMarker:
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
                if not numpy.allclose(scaledData,scaledOtherData,rtol,atol):
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
                if not numpy.allclose(scaledError,otherScaledError,rtol,atol):
                    _logger.debug('The errors differ: %s\n%s' % (scaledError,otherScaledError))
                    return False
        else:
            if not data.dtype.char in ['S','U']:
                try:
                    scaledData = data*self.unit
                    scaledOtherData = otherData*other.unit
                    if not numpy.allclose(scaledData,scaledOtherData,rtol,atol):
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
                    if not numpy.allclose(scaledError,otherScaledError,rtol,atol):
                        _logger.debug('The errors differ: %s\n%s' % (scaledError,otherScaledError))
                        return False
        if not self.attributes == other.attributes:
            _logger.debug('The attribute dictionary differs.')
            return False
        for dimSelf,dimOther in zip(self._dimensions,other.dimensions):
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
            if len(self._dimensions) != len(other.dimensions):
                return NotImplemented
            for i in xrange(len(self._dimensions)):
                if not self._dimensions[i] == other.dimensions[i]:
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
                                  copy.deepcopy(self._dimensions),
                                  longname, shortname)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, FieldContainer):
            if self.error!=None or other.error!=None:
                return NotImplemented
            else:
                error = None
            if len(self._dimensions) != len(other.dimensions):
                return NotImplemented
            for i in xrange(len(self._dimensions)):
                if not self._dimensions[i] == other.dimensions[i]:
                    return NotImplemented
            if isPhysicalQuantity(self.unit):
                if not (isPhysicalQuantity(other.unit) and self.unit.isCompatible(other.unit.unit)):
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
                                  copy.deepcopy(self._dimensions),
                                  longname, shortname)
        return NotImplemented

    def __str__(self):
        deps = [ dim for dim in self._dimensions if type(dim)!=type(IndexMarker()) ]
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
        if isinstance(args, type(1)):
            if args>=len(self.data):
                raise IndexError, 'index out of bound'
        try:
            len(args)
        except:
            args = [args]
        args = [ slice2ind(arg, self._dimensions[dim]) for dim, arg in enumerate(args) ]
        data = self.data[args]
        attributes = copy.deepcopy(self.attributes)
        mask = None
        error = None
        dimensions = []
        for i,l in enumerate(data.shape[:len(args)]):
            dim = self._dimensions[i]
            if l==1:
                attributes[dim.longname] = (dim.shortname, dim.data[args[i]].squeeze()*dim.unit)
            else:
                if isinstance(dim, IndexMarker):
                    dimensions.append(dim)
                else:
                    dimensions.append(dim[args[i],])
        for i in xrange(len(args),len(data.shape)):
            dimensions.append(copy.deepcopy(self._dimensions[i]))
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
        # Valid dimensions?
        if (not (len(self._dimensions)==1
                 and isinstance(self._dimensions[0], IndexMarker)) #IndexMarkers are valid and...
            and not (self.data.shape == (1,) and len(self._dimensions)==0)): #...so are zero dim fields.
            dimshape = []
            for d in self._dimensions:
                if len(d.data.shape)>1:
                    _logger.debug("Dimension %s is not 1-d." % d.longname)
                    return False
                dimshape.append(d.data.shape[0])
            if self.data.shape!=tuple(dimshape):
                _logger.debug("Shape of data %s and of dimensions %s do not match for field\n:%s" %
                              (self.data.shape, dimshape, self))
                return False
            for d in self._dimensions:
                if not d.isValid():
                    _logger.debug("Invalid dimension %s."%d.longname)
                    return False
        # Valid mask?
        if (self.mask!=None) and (self.data.shape!=self.mask.shape):
            _logger.debug("Shape of data %s and of mask %s do not match."%(self.data.shape, self.mask.shape))
            return False
        # Valid error?
        if (self.error!=None) and (self.data.shape!=self.error.shape):
            _logger.debug("Shape of data %s and of error %s do not match."%(self.data.shape, self.error.shape))
            return False
        return True

    def isIndex(self):
        return self.dimensions==INDEX

    def isIndependent(self):
        for d in self.dimensions:
            if not d.isIndex():
                return False
        return True

    def isLinearlyDiscretised(self):
        for dim in self.dimensions:
            d = numpy.diff(dim.data)
            if not numpy.alltrue(numpy.logical_not(d-d[0])):
                return False
        return True

    maskedData = property( lambda self: numpy.ma.array(self.data, mask=self.mask) )
    maskedError = property( lambda self: numpy.ma.array(self.error, mask=self.mask) )

