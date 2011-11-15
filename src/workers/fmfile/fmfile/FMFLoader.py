# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
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
The FMF Loader is a class of Pyphant's FMF Toolbox. It loads an FMF
file from the location given in the worker's configuration.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import zipfile
import numpy
import re
import copy
import StringIO
import os.path
import codecs
from pyphant.core import (Worker, Connectors, DataContainer)
from pyphant.quantities import (Quantity, isQuantity)
from pyphant.quantities.ParseQuantities import (parseQuantity, parseVariable,
                                                parseDateTime, str2unit)
import logging
_logger = logging.getLogger("pyphant")

def normation(normationStr):
    try:
        unit = Quantity(str(normationStr))
    except:
        try:
            unit = Quantity(1.0, str(normationStr))
        except:
            unit = float(normationStr)
    return unit

def loadDataFromZip(filename, subscriber=1):
    z = zipfile.ZipFile(filename, 'r')
    names = z.namelist()
    names.sort()
    total = len(names)
    assert total > 0, "The loaded FMF archive named %s \
                        does not contain any files." % filename
    data = {}
    for i, pixelName in enumerate(names):
        b = z.read(pixelName)
        rawContainer = readSingleFile(b, pixelName)
        if len(rawContainer) == 1:
            data[pixelName] = rawContainer[0]
        else:
            data[pixelName] = rawContainer
        subscriber %= float(i + 1) / total * 100.0
    return data, names

def collectAttributes(data, names):
    """Function collectAttributes(data)
    data: dictionary referencing the FMF attributes by the respective filenames
    returns tuple (dictionary of common attributes, dictionary of variable
    attributes).
    """
    #Collect attributes, define filename as new attribute
    atts = {u'filename': names}
    for filename in names:
        sc = data[filename]
        for section, sectionDict in sc.attributes.iteritems():
            for key, treetoken in sectionDict.iteritems():
                attlist = atts.setdefault(key, [])
                attlist.append(treetoken)
    #Separate common attributes from variable attributes
    commonAttr = {}
    variableAttr = {}
    for k, l in atts.iteritems():
        v = l[0]
        isConst = True
        for i in l[1:]:
            if i != v:
                isConst = False
                #break
        if isConst:
            commonAttr[k] = v
        else:
            variableAttr[k] = l
    return (commonAttr, variableAttr)


class column2Field:
    def __init__(self):
        self.Np = 0
        self.Nt = 0

    def norm(self, datum, unit, error=False):
        if isQuantity(datum):
            try:
                return datum.inUnitsOf(unit).value
            except:
                raise ValueError, "The datum %s cannot be expressed \
                                    in terms of %s." % (datum, unit)
        elif error:
            return 0.0
        else:
            return numpy.NaN

    def __call__(self, longname, column):
        tupples = filter(lambda c: type(c) == type((0,)), column)
        hasTupples = len(tupples) > 0
        if hasTupples:
            tuppleLength = max(map(len, tupples))
        if hasTupples:
            if tuppleLength == 2:
                indexDatum = 0
                indexError = 1
                if isQuantity(tupples[0][1]) and tupples[0][1].isCompatible('s'):
                    shortname = 't_%i' % self.Nt
                    self.Nt += 1
                else:
                    shortname = 'p_%i' % self.Np
                    self.Np += 1
                for i, element in enumerate(column):
                    if not type(element) == type((0,)):
                        column[i] = (numpy.NaN, None)
            elif tuppleLength == 3:
                shortname = tupples[0][0]
                indexDatum = 1
                indexError = 2
                for i, element in enumerate(column):
                    if not type(element) == type((0,)):
                        column[i] = (shortname, numpy.NaN, None)
            try:
                data = [element[indexDatum] for element in column]
            except:
                print longname, column
                import sys
                sys.exit(0)
            error = [element[indexError] for element in column]
            unitCandidates = [element.unit for element in data \
                              if isQuantity(element)]
            if len(unitCandidates) == 0:
                unit = 1.0
            else:
                unit = unitCandidates[0]
            normation = lambda arg: self.norm(arg, unit)
            field = numpy.array(map(normation, data))
            ErrorNormation = lambda arg: self.norm(arg, unit, error=True)
            result = DataContainer.FieldContainer(field,
                                error=numpy.array(map(ErrorNormation, error)),
                                mask=numpy.isnan(field),
                                unit=Quantity(1.0, unit),
                                shortname=shortname,
                                longname=longname)
        else:
            #Joining lists of strings
            if type(column[0]) == type([]):
                firstElement = column[0][0]
            else:
                firstElement = column[0]
            if type(firstElement) in (type(''), type(u'')):
                for i in xrange(len(column)):
                    if type(column[i]) == type([]):
                        column[i] = ','.join(column[i])
            result = DataContainer.FieldContainer(numpy.array(column),
                                                  longname=longname)
        return result
column2FieldContainer = column2Field()

def unpackAndCollateFields(variableAttr, data):
    fieldData = {}
    dependencies = {}
    units = {}
    shortnames = {}
    for filename in variableAttr['filename']:
        sample = data[filename]
        for field in sample.columns:
            if field.longname in fieldData:
                conversionFactor = normation(field.unit) / units[field.longname]
                fieldData[field.longname].append(field.data * conversionFactor)
                dimensionNames = [dim.longname for dim in field.dimensions
                                  if dim.longname != u'Index']
                if len(dimensionNames) > 1:
                    _logger.warning("Is specified, but has not been tested!")
                if dependencies[field.longname] != dimensionNames:
                    raise ValueError, "The data sets of the FMF archive have \
                                        inconsistent dependencies in section \
                                        [*data definitions]."
            else:
                fieldData[field.longname] = [field.data]
                dependencies[field.longname] = [dim.longname for dim
                                                in field.dimensions
                                                if dim.longname != u'Index']
                units[field.longname] = normation(field.unit)
                shortnames[field.longname] = field.shortname
    return fieldData, dependencies, units, shortnames

def checkAndCondense(data):
    reference = data[0]
    for element in data[1:]:
        numpy.testing.assert_array_almost_equal(reference, element)
    return reference

def readZipFile(filename, subscriber=1):
    data, names = loadDataFromZip(filename, subscriber)
    commonAttr, variableAttr = collectAttributes(data, names)
    #Wrap variable attributes into FieldContainer
    containers = [column2FieldContainer(longname, column) for longname, column
                  in variableAttr.iteritems()]
    #Process SampleContainers of parsed FMF files and skip independent
    #variables, which are used as dimensions.
    fieldData, dependencies, units, shortnames = unpackAndCollateFields(
        variableAttr, data)
    independentFieldsNames = []
    for fieldName, dependency in dependencies.iteritems():
        if dependencies[fieldName] == []:
            independentFieldsNames.append(fieldName)
    for fieldName in independentFieldsNames:
        del dependencies[fieldName]
    #Build independent fields
    independentFields = {}
    for indepField in independentFieldsNames:
        indepData = checkAndCondense(fieldData[indepField])
        independentFields[indepField] = DataContainer.FieldContainer(
                                            numpy.array(indepData),
                                            longname=indepField,
                                            shortname=shortnames[indepField],
                                            unit=units[indepField],
                                            rescale=True
                                            )
    #Build dependent fields
    #QUESTION: Can a field depend on a dependent field?
    for field, dependency in dependencies.iteritems():
        newField = DataContainer.FieldContainer(numpy.array(fieldData[field]),
                                                longname=field,
                                                shortname=shortnames[field],
                                                unit=units[field],
                                                rescale=True)
        for i, indepField in enumerate(dependency):
            dim = len(newField.dimensions) - i - 1
            newField.dimensions[dim] = independentFields[indepField]
        assert newField.isValid()
        containers.append(newField)
    #The next lines are a hack and should be dealt with properly...
    if u'creator' in commonAttr.keys():
        creator = commonAttr[u'creator']
        del commonAttr[u'creator']
        result = DataContainer.SampleContainer(containers,
                                               attributes=commonAttr)
        result.creator = creator
    else:
        result = DataContainer.SampleContainer(containers,
                                               attributes=commonAttr)
    return result

def reshapeField(field):
    if field.isIndependent() or len(field.dimensions) == 1:
        return field
    dimData = [numpy.unique(d.data) for d in field.dimensions]
    dimDicts = [dict([(data, index) for index, data in enumerate(dimdata)])
                for dimdata in dimData]
    fieldData = numpy.ones([len(d) for d in dimData]) * numpy.nan
    indicess = zip(*[map(lambda x: dimDicts[index][x], dim.data) \
                     for index, dim in enumerate(field.dimensions)])
    for datum, indices in zip(field.data, indicess):
        fieldData[indices] = datum
    newDims = [ DataContainer.FieldContainer(dimData[i],
                                             f.unit,
                                             longname=f.longname,
                                             shortname=f.shortname,
                                             attributes=f.attributes)
                for i, f in enumerate(field.dimensions) ]
    newField = DataContainer.FieldContainer(fieldData,
                                            field.unit,
                                            mask=numpy.isnan(fieldData),
                                            dimensions=newDims,
                                            longname=field.longname,
                                            shortname=field.shortname,
                                            attributes=field.attributes)
    return newField

def readDataFile(filename):
    filehandle = open(filename, 'r')
    dat = filehandle.read()
    filehandle.close()
    rawContainer = readSingleFile(dat, filename)
    if len(rawContainer) == 1:
        container = rawContainer[0]
        container.seal()
        return container
    newSample = DataContainer.SampleContainer(rawContainer,
                        longname='List of tables',
                        shortname='L',
                        attributes=copy.deepcopy(rawContainer[0].attributes))
    newSample.seal()
    return newSample

def loadFMFFromFile(filename, subscriber=0):
    try:
        return readZipFile(filename, subscriber=subscriber)
    except zipfile.BadZipfile:
        return readDataFile(filename)

def readSingleFile(b, pixelName):
    _logger.info(u"Parsing file %s." % pixelName)
    preParsedData, d, FMFversion, commentChar = preParseData(b)
    from configobj import ConfigObj, ConfigObjError
    class FMFConfigObj(ConfigObj):
        #   ConfigObj sets the following default
        #   in opposition to FMF
        #   Function            ConfigObj   FMF
        #   Key-Value-Seperator "="         ":"
        #   CommentChar         "#"         "#",";", ....
        #
        #   So we have to redefine our regexp
        #
        _keyword = re.compile(r'''^ # line start
            (\s*)                   # indentation
            (                       # keyword
                (?:".*?")|          # double quotes
                (?:'.*?')|          # 'single quotes
                (?:[^'":].*?)       # no quotes
            )
            \s*:\s*                 # divider
            (.*)                    # value (including list values and comments)
            $   # line end
            ''', re.VERBOSE)  #'

        _sectionmarker = re.compile(r'''^
            (\s*)                     # 1: indentation
            ((?:\[\s*)+)              # 2: section marker open
            (                         # 3: section name open
                (?:"\s*\S.*?\s*")|    # at least one non-space with double quotes
                (?:'\s*\S.*?\s*')|    # at least one non-space with single quotes
                (?:[^'"\s].*?)        # at least one non-space unquoted
            )                         # section name close
            ((?:\s*\])+)              # 4: section marker close
            \s*(%s.*)?                # 5: optional comment
            $''' % commentChar,
            re.VERBOSE)

        _valueexp = re.compile(r'''^
            (?:
                (?:
                    (
                        (?:
                            (?:
                                (?:".*?")|              # double quotes
                                (?:'.*?')|              # single quotes
                                (?:[^'",%s][^,%s]*?)    # unquoted
                            )
                            \s*,\s*                     # comma
                        )*      # match all list items ending in a comma (if any)
                    )
                    (
                        (?:".*?")|                      # double quotes
                        (?:'.*?')|                      # single quotes
                        (?:[^'",%s\s][^,]*?)|  # unquoted
                        (?:(?<!,))                      # Empty value
                    )?          # last item in a list - or string value
                )|
                (,)             # alternatively a single comma - empty list
            )
            \s*(%s.*)?          # optional comment
            $''' % ((commentChar, )*4),
            re.VERBOSE)
    
        # use findall to get the members of a list value
        _listvalueexp = re.compile(r'''
            (
                (?:".*?")|          # double quotes
                (?:'.*?')|          # single quotes
                (?:[^'",%s]?.*?)       # unquoted
            )
            \s*,\s*                 # comma
            ''' % commentChar,
            re.VERBOSE)
    
        # this regexp is used for the value
        # when lists are switched off
        _nolistvalue = re.compile(r'''^
            (
                (?:".*?")|          # double quotes
                (?:'.*?')|          # single quotes
                (?:[^'"%s].*?)|     # unquoted
                (?:)                # Empty value
            )
            \s*(%s.*)?              # optional comment
            $''' % (commentChar, commentChar),
            re.VERBOSE)
    
        # regexes for finding triple quoted values on one line
        _single_line_single = re.compile(
                                r"^'''(.*?)'''\s*(%s.*)?$" % commentChar, 
                                re.VERBOSE)
        _single_line_double = re.compile(
                                r'^"""(.*?)"""\s*(%s.*)?$' % commentChar, 
                                re.VERBOSE)
        _multi_line_single = re.compile(
                                r"^(.*?)'''\s*(%s.*)?$" % commentChar, 
                                re.VERBOSE)
        _multi_line_double = re.compile(
                                r'^(.*?)"""\s*(%s.*)?$' % commentChar, 
                                re.VERBOSE)
    try:
        config = FMFConfigObj(d.encode('utf-8').splitlines(), encoding='utf-8')
    except ConfigObjError, e:
        from sys import exit
        exit('%s\nPlease check the syntax of the FMF-file, in particular \
                the correct usage of comments.' % e)
    return config2tables(preParsedData, config, FMFversion)

def parseBool(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    raise AttributeError

def getConverters(FMFversion='1.1'):
    converters = [
        int,
        float,
        parseBool,
        lambda v: parseVariable(v,FMFversion),
        lambda q: parseQuantity(q,FMFversion),
        complex,        # Complex is checked after variables and quantities,
                        # because 1J is 1 Joule and not an imaginary number.
        lambda d: parseDateTime(d,FMFversion),
        ]
    return converters

def item2value(oldVal, FMFversion='1.1'):
    if type(oldVal) == type([]):
        for c in getConverters(FMFversion):
            try:
                return map(c, oldVal)
            except:
                pass
    for c in getConverters(FMFversion):
        try:
            return c(oldVal)
        except:
            pass
    return oldVal

def config2tables(preParsedData, config, FMFversion='1.1'):
    if config.has_key('*table definitions'):
        longnames = dict([(i, k) for k, i
                          in config['*table definitions'].iteritems()])
        del config['*table definitions']
    else:
        longnames = { None : 'Table' }
    tables = []
    for k in config:
        if k.startswith('*data definitions'):
            if k == '*data definitions':
                shortname = None
            else:
                shortname = k.split(':')[1].strip()
            tables.append(data2table(longnames[shortname],
                                     shortname,
                                     preParsedData[shortname],
                                     config[k],FMFversion))
            del config[k]
    attributes = config.walk(lambda section, key:
                             item2value(section[key], FMFversion))
    for t in tables:
        t.attributes = copy.deepcopy(attributes)
    return tables

def data2table(longname, shortname, preParsedData, config, FMFversion='1.1'):
    datTable = []
    shapelen = len(preParsedData.shape)
    if len(config) == 1:
        if shapelen == 0:
            preParsedData = preParsedData.reshape((1, 1))
        elif shapelen == 1:
            preParsedData = preParsedData.reshape((1, preParsedData.shape[0]))
    else:
        if shapelen == 1:
            preParsedData = preParsedData.reshape((preParsedData.shape[0], 1))
    assert len(preParsedData.shape) == 2
    for col in preParsedData:
        try:
            result = col.astype('i')
        except ValueError, e:
            try:
                result = col.astype('f')
            except ValueError, e:
                try:
                    result = col.astype('complex')
                except ValueError, e:
                    result = col
        datTable.append(result)
    colspec_re = re.compile(ur"(?P<shortname>[^\s([]*)\s*(?P<deps>\([^)]*\))?\s*(?:(?:\\pm|\+-|\+/-)\s*(?P<error>[^\s[]*))?\s*(?P<unit>\[[^]]*])?")
    fields = []
    fields_by_name = {}
    dimensions_for_fields = {}
    errors_for_fields = {}
    for i, (fieldLongname, spec) in enumerate(config.items()):
        if type(spec) == type([]):
            spec = ','.join(spec)
        try:
            match = re.search(colspec_re, spec)
        except TypeError, e:
            _logger.error("""Cannot interpret definition of data column "%s", \
                            which is given as "%s"!""" % (fieldLongname, spec))
        unit = match.group('unit')
        if unit != None:
            unit = str2unit(unit[1: -1], FMFversion)
        else:
            unit = 1.0
        fieldShortname = match.group('shortname')
        dimensions = match.group('deps')
        if dimensions != None:
            dimensions_for_fields[fieldShortname] = dimensions[1: -1].split(',')
        else:
            dimensions_for_fields[fieldShortname] = None
        errors_for_fields[fieldShortname] = match.group('error')
        field = DataContainer.FieldContainer(datTable[i],
                                             longname=fieldLongname,
                                             shortname=fieldShortname,
                                             unit=unit)
        fields.append(field)
        fields_by_name[fieldShortname] = field
    for f in fields:
        sn = f.shortname
        dims = dimensions_for_fields[sn]
        if dims != None:
            f.dimensions = [fields_by_name[d] for d in dims]
        error = errors_for_fields[sn]
        if error != None:
            try:
                error = float(error)
                f.error = numpy.ones(f.data.shape) * error
            except:
                f.error = fields_by_name[error].inUnitsOf(f).data
    reshapedFields = []
    for field in fields:
        try:
            newField = reshapeField(field)
        except TypeError:
            raise
            if field.data.dtype.name.startswith('string'):
                _logger.warning('Warning: Cannot reshape numpy.array \
                                   of string: %s' % field)
                newField = field
            else:
                _logger.error('Error: Cannot reshape numpy.array: %s' % field)
                import sys
                sys.exit(0)
        reshapedFields.append(newField)
    if shortname == None:
        shortname = 'T'
    return DataContainer.SampleContainer(reshapedFields,
                                         longname=longname,
                                         shortname=shortname)

def preParseData(b):
    localVar = {'fmf-version':'1.1', 'coding':'utf-8', 'delimiter':'\t'}
    commentChar = ';'
    if b.startswith(codecs.BOM_UTF8):
        b = b.lstrip(codecs.BOM_UTF8)
    if b[0] == ';' or b[0] == '#':
        commentChar = b[0]
        items =  [var.strip().split(':') for var
                  in b.split('-*-')[1].split(';')]
        try:
            for key, value in items:
                localVar[key.strip()] = value.strip()
                if localVar[key.strip()] == 'whitespace':
                    localVar[key.strip()] = None
                if localVar[key.strip()] == 'semicolon':
                    localVar[key.strip()] = ';'
        except ValueError, e:
            from sys import exit
            exit('%s\nPlease, check syntax of headline, presumably a key \
                    and its value are not separated by a colon.' % e)
    d = unicode(b, localVar['coding'])
    dataExpr = re.compile(ur"^(\[\*data(?::\s*([^\]]*))?\]\r?\n)([^[]*)",
                          re.MULTILINE | re.DOTALL)
    commentExpr = re.compile(ur"^%s.*"%commentChar, re.MULTILINE)
    d = re.sub(commentExpr, '', d)
    preParsedData = {}
    def preParseData(match):
        try:
            preParsedData[match.group(2)] = numpy.loadtxt(
                                            StringIO.StringIO(match.group(3)),
                                            unpack=True,
                                            comments=commentChar,
                                            dtype='S',
                                            delimiter=localVar['delimiter']
                                            )
        except Exception:
            return match.group(0)
        return u""
    d = re.sub(dataExpr, preParseData, d)
    return preParsedData, d, str(localVar['fmf-version']), commentChar


class FMFLoader(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Load FMF files"

    _params = [("filename", u"Filename", "", Connectors.SUBTYPE_FILE)]

    def inithook(self):
        fileMask = "FMF and FMF-ZIP (*.fmf, *.zip)|*.fmf;*.zip|FMF (*.fmf)|" \
                   "*.fmf|FMF-ZIP (*.zip)|*.zip|All files (*)|*"
        self.paramFilename.fileMask = fileMask

    @Worker.plug(Connectors.TYPE_ARRAY)
    def loadFMF(self, subscriber=0):
        filename = self.paramFilename.value
        if not os.path.exists(filename):
            raise RuntimeError("Opening non existent file: "+filename)
        result = loadFMFFromFile(filename, subscriber)
        result.seal()
        return result
