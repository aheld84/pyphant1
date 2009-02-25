# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import zipfile, numpy, re, collections, copy, StringIO, os.path
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity,isPhysicalUnit,isPhysicalQuantity
from pyphant.quantities.ParseQuantities import parseQuantity, parseVariable, str2unit
import mx.DateTime.ISO
import logging
_logger = logging.getLogger("pyphant")

def normation(normationStr):
    try:
        unit = PhysicalQuantity(str(normationStr))
    except:
        try:
            unit = PhysicalQuantity(1.0,str(normationStr))
        except:
            unit = float(normationStr)
    return unit

def loadDataFromZip(filename, subscriber=1):
    z = zipfile.ZipFile(filename, 'r')
    names = z.namelist()
    total = len(names)
    assert total>0, "The loaded FMF archive named %s does not contain any files." % filename
    data = {}
    for i,pixelName in enumerate(names):
        b = z.read(pixelName)
        rawContainer = readSingleFile(b, pixelName)
        if len(rawContainer)==1:
            data[pixelName] = rawContainer[0]
        else:
            data[pixelName] = rawContainer
        subscriber %= float(i+1)/total*100.0
    return data

def collectAttributes(data):
    #Collect attributes, define filename as new attribute
    atts = {u'filename': []}
    for filename,sc in data.iteritems():
        atts['filename'].append(filename)
        for section,sectionDict in sc.attributes.iteritems():
            for key,treetoken in sectionDict.iteritems():
                attlist = atts.setdefault(key, [])
                attlist.append(treetoken)
    #Separate common attributes from variable attributes
    commonAttr = {}
    variableAttr = {}
    for k,l in atts.iteritems():
        v = l[0]
        isConst=True
        for i in l[1:]:
            if i!=v:
                isConst=False
                #break
        if isConst:
            commonAttr[k]=v
        else:
            variableAttr[k]=l
    return (commonAttr, variableAttr)

def column2FieldContainer(longname, column):
    if type(column[0])==type((0,)) and len(column[0])==3:
        shortname = column[0][0]
        if isPhysicalQuantity(column[0][1]):
            unit = column[0][1].unit
            field = [row[1].inUnitsOf(unit).value for row in column]
        else:
            unit = 1.0
            field = [row[1] for row in column]
        result = DataContainer.FieldContainer(numpy.array(field),unit=PhysicalQuantity(1.0, unit),shortname=shortname,longname=longname)
    else:
        result = DataContainer.FieldContainer(numpy.array(column),longname=longname)
    return result

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
                                  if dim.longname!=u'Index']
                if len(dimensionNames)>1:
                    _logger.warning("Is specified, but has not been tested!")
                if dependencies[field.longname] != dimensionNames:
                    raise ValueError, "The data sets of the FMF archive have inconsistent dependencies in section [*data definitions]."
            else:
                fieldData[field.longname]=[field.data]
                dependencies[field.longname]=[dim.longname for dim in field.dimensions
                                               if dim.longname!=u'Index']
                units[field.longname] = normation(field.unit)
                shortnames[field.longname]=field.shortname
    return fieldData, dependencies, units, shortnames

def checkAndCondense(data):
    reference = data[0]
    for element in data[1:]:
        numpy.testing.assert_array_almost_equal(reference, element)
    return reference

def readZipFile(filename, subscriber=1):
    data = loadDataFromZip(filename, subscriber)
    commonAttr, variableAttr = collectAttributes(data)
    #Wrap variable attributes into FieldContainer
    containers = [ column2FieldContainer(longname, column) for longname, column in variableAttr.iteritems()]
    #Process SampleContainers of parsed FMF files and skip independent variables, which are used as dimensions.
    fieldData, dependencies, units, shortnames = unpackAndCollateFields(variableAttr, data)
    independentFieldsNames = []
    for fieldName,dependency in dependencies.iteritems():
        if dependencies[fieldName]==[]:
            independentFieldsNames.append(fieldName)
    for fieldName in independentFieldsNames:
        del dependencies[fieldName]
    #Build independent fields
    independentFields = {}
    for indepField in independentFieldsNames:
        indepData = checkAndCondense(fieldData[indepField])
        independentFields[indepField] = DataContainer.FieldContainer(numpy.array(indepData),
                                                                     longname=indepField,shortname=shortnames[indepField],
                                                                     unit = units[indepField],rescale=True)
    #Build dependent fields
    #QUESTION: Can a field depend on a dependent field?
    for field,dependency in dependencies.iteritems():
        newField = DataContainer.FieldContainer(numpy.array(fieldData[field]),
                                                longname=field,
                                                shortname=shortnames[field],
                                                unit = units[field],rescale=True)
        for i,indepField in enumerate(dependency):
            dim = len(newField.dimensions)-i-1
            newField.dimensions[dim]=independentFields[indepField]
        assert newField.isValid()
        containers.append(newField)
    return DataContainer.SampleContainer(containers,attributes=commonAttr)

def reshapeField(field):
    if field.isIndependent():
        return field
    dimData = [numpy.unique(d.data) for d in field.dimensions]
    fieldData = numpy.ones([len(d) for d in dimData])*numpy.nan
    data = numpy.vstack([field.data]+[d.data for d in field.dimensions]).transpose()
    for row in data:
        try:
            fieldData[[numpy.argwhere(dimData[i]==v) for i,v in enumerate(row[1:])]] = row[0]
        except AttributeError:
            from pyphant.wxgui2.wxPyphantApplication import LOGDIR
            import os, os.path
            DEBDIR=os.path.join(LOGDIR, "pyphant_debug")
            if not os.path.exists(DEBDIR):
                os.mkdir(DEBDIR)
            for i,v in enumerate(row[1:]):
                try:
                    numpy.argwhere(dimData[i]==v)
                except AttributeError, e:
                    _logger.debug(u"AttributeError occured:",
                                  exc_info=True)
                    f = open(os.path.join(DEBDIR, "deblog"), 'w')
                    f.write("dShape: %s; vShape: %s\n\n"%(dimData[i].shape, v.shape))
                    f.write("%s"%dimData[i])
                    f.write("\n\nv:\n")
                    f.write("%s"%v)
                    f.write("\n")
                    f.close()
                    numpy.savetxt(os.path.join(DEBDIR, "dimData.txt"), dimData[i])
                    numpy.savetxt(os.path.join(DEBDIR, "data.txt"), data)
                    numpy.savetxt(os.path.join(DEBDIR, "row.txt"), row)
                    numpy.savetxt(os.path.join(DEBDIR, "v.txt"), v)
                    raise
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
    filehandle = open(filename,'r')
    dat = filehandle.read()
    filehandle.close()
    rawContainer = readSingleFile(dat,filename)
    if len(rawContainer)==1:
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
    preParsedData, d = preParseData(b)
    from configobj import ConfigObj
    class FMFConfigObj(ConfigObj):
        _keyword = re.compile(r'''^ # line start
            (\s*)                   # indentation
            (                       # keyword
                (?:".*?")|          # double quotes
                (?:'.*?')|          # single quotes
                (?:[^'":].*?)       # no quotes
            )
            \s*:\s*                 # divider
            (.*)                    # value (including list values and comments)
            $   # line end
            ''', re.VERBOSE)
    from StringIO import StringIO
    config = FMFConfigObj(d.encode('utf-8').splitlines(), encoding='utf-8')
    return config2tables(preParsedData, config)

def parseBool(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    raise AttributeError

def config2tables(preParsedData, config):
    converters = [
        int,
        float,
        complex,
        parseBool,
        parseQuantity,
        parseVariable,
        lambda d: str(mx.DateTime.ISO.ParseAny(d))
        ]

    def item2value(section, key):
        oldVal = section[key]
        if type(oldVal)==type([]):
            for c in converters:
                try:
                    return map(c,oldVal)
                except:
                    pass
        for c in converters:
            try:
                return c(oldVal)
            except:
                pass
        return oldVal

    if config.has_key('*table definitions'):
        longnames = dict([(i,k) for k,i in config['*table definitions'].iteritems()])
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
                                     config[k]))
            del config[k]
    attributes = config.walk(item2value)
    for t in tables:
        t.attributes = copy.deepcopy(attributes)
    return tables

def data2table(longname, shortname, preParsedData, config):
    datTable = []
    for col in preParsedData:
        try:
            result = col.astype('i')
        except ValueError,e:
            try:
                result = col.astype('f')
            except ValueError,e:
                try:
                    result = col.astype('complex')
                except ValueError,e:
                    result = col
        datTable.append(result)
    colspec_re = re.compile(ur"(?P<shortname>[^\s([]*)\s*(?P<deps>\([^)]*\))?\s*(?:(?:\\pm|\+-|\+/-)\s*(?P<error>[^\s[]*))?\s*(?P<unit>\[[^]]*])?")
    fields = []
    fields_by_name = {}
    dimensions_for_fields = {}
    errors_for_fields = {}
    for i, (fieldLongname, spec) in enumerate(config.items()):
        if type(spec)==type([]):
            spec = ','.join(spec)
        try:
            match = re.search(colspec_re, spec)
        except TypeError,e:
            _logger.error("""Cannot interpret definition of data column "%s", which is given as "%s"!""" % (fieldLongname,spec))
        unit = match.group('unit')
        if unit != None:
            unit = str2unit(unit[1:-1])
        else:
            unit = 1.0
        fieldShortname=match.group('shortname')
        dimensions = match.group('deps')
        if dimensions != None:
            dimensions_for_fields[fieldShortname] = dimensions[1:-1].split(',')
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
            f.dimensions = [ fields_by_name[d] for d in dims ]
        error = errors_for_fields[sn]
        if error != None:
            try:
                error = float(error)
                f.error = numpy.ones(f.data.shape)*error
            except:
                f.error = fields_by_name[error].inUnitsOf(f).data
    fields = [ reshapeField(field) for field in fields ]
    if shortname==None:
        shortname='T'
    return DataContainer.SampleContainer(fields,
                                         longname=longname,
                                         shortname=shortname)


def preParseData(b):
    localVar = {'fmf-version':'1.0','coding':'cp1252',
                'delimiter':'\t'}
    commentChar = ';'
    if b[0] == ';' or b[0] == '#':
        commentChar = b[0]
        items =  [var.strip().split(':') for var in b.split('-*-')[1].split(';')]
        for key,value in items:
            localVar[key.strip()]=value.strip()
            if localVar[key.strip()]=='whitespace':
                localVar[key.strip()] = None
            if localVar[key.strip()]=='semicolon':
                localVar[key.strip()] = ';'
    d = unicode(b, localVar['coding'])
    dataExpr = re.compile(ur"^(\[\*data(?::\s*([^\]]*))?\]\r?\n)([^[]*)", re.MULTILINE | re.DOTALL)
    commentExpr = re.compile(ur"^%s.*"%commentChar, re.MULTILINE)
    d = re.sub(commentExpr, '', d)
    preParsedData = {}
    def preParseData(match):
        try:
            preParsedData[match.group(2)] = numpy.loadtxt(StringIO.StringIO(match.group(3)),
                                                          unpack=True,
                                                          comments=commentChar,
                                                          dtype='S',
                                                          delimiter=localVar['delimiter'])
        except Exception, e:
            return match.group(0)
        return u""
    d = re.sub(dataExpr, preParseData, d)
    return preParsedData, d

class FMFLoader(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Load FMF files"

    _params=[("filename", u"Filename", "", Connectors.SUBTYPE_FILE)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def loadFMF(self, subscriber=0):
        filename = self.paramFilename.value
        if not os.path.exists(filename):
            raise RuntimeError("Opening non existant file: "+filename)
        result = loadFMFFromFile(filename, subscriber)
        result.seal()
        return result

