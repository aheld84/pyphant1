# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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
"""

__version__ = "$Revision$"
# $Source$

import zipfile, numpy, re, collections
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

from pyphant import quantities

def makeRoot(pixelName, ll):
    return {}

def startSection(root, dataSections, l):
    if l == u'MESSDATEN':
        root[l] = []
    elif l == u'SPALTENBESCHRIFTUNG':
        root[l] = []
    else:
        root[l] = {}
        dataSections.append(l)
    return root[l], l

def addAttributeLine(section, l):
    ff = l.split('=')
    section[ff[0]] = ff[1]

def addDataColumn(section, l):
    ff = l.split('=')
    section.append(ff[1])

def addTableLine(section, l):
    ff = l.split()
    section.append([float(f) for f in ff])

LINE_HANDLER = collections.defaultdict(lambda :addAttributeLine)
LINE_HANDLER[u'Section']=startSection
LINE_HANDLER[u'SPALTENBESCHRIFTUNG']=addDataColumn
LINE_HANDLER[u'MESSDATEN']=addTableLine

def readZipFile(filename, data=None, subscriber=0):
    if data == None:
        data = []
    z = zipfile.ZipFile(filename, 'r')
    names = z.namelist()
    total = len(names)
    for i,pixelName in enumerate(names):
        b = z.read(pixelName)
        root, dataSections = readSingleFile(b, pixelName)
        data.append(root)
        subscriber %= float(i)/total*100.0
    return data,dataSections

def readDataFile(filename,data=None):
    if data==None:
        data = []
    filehandle = open(filename,'r')
    dat = filehandle.read()
    filehandle.close()
    root, dataSections = readSingleFile(dat,filename)
    data.append(root)
    return data,dataSections

def createFieldContainer(key,array):
    def longname2unit(name):
        reg = re.compile(r"\[([^]]*)\]")
        m = reg.search(name)
        if not m or m.group(1)=="counts" or m.group(1)=="":
            return 1.0
        else:
            return quantities.Quantity('1 '+str(m.group(1)))
    fieldUnit = longname2unit(key)
    if quantities.isQuantity(fieldUnit):
        fieldContainer = DataContainer.FieldContainer(numpy.array(array), unit=fieldUnit, longname=key)
    else:
        try:
            quantities = [quantities.Quantity(string.encode('latin-1')) for string in array]
            firstUnit = quantities[0].unit
            scaledArray = [quant.inUnitsOf(firstUnit).value for quant in quantities]
            fieldContainer = DataContainer.FieldContainer(numpy.array(scaledArray), unit='1. %s' % firstUnit.name(),
                                                          longname=key)
        except:
            fieldContainer = DataContainer.FieldContainer(numpy.array(array), unit=fieldUnit, longname=key)
    return fieldContainer

def loadOscFromFile(filename, subscriber=0):
    try:
        data,dataSections = readZipFile(filename, subscriber=subscriber)
    except zipfile.BadZipfile:
        data,dataSections = readDataFile(filename)
    container = constructTemplate(data, dataSections)
    for d in data:
        for dicname in dataSections:
            for k in d[dicname].keys():
                container[k].append(d[dicname][k])
        for i, col in enumerate(d[u'SPALTENBESCHRIFTUNG']):
            container[col].append(d[u'MESSDATEN'][:,i])
    cols = [createFieldContainer(k,v) for k,v in container.iteritems()]
    if container.has_key('KOMMENTAR'):
        title=container[u'KOMMENTAR'][0]
    else:
        title=''
    return DataContainer.SampleContainer(cols, longname=title)

def constructTemplate(data, dataSections):
    template = data[0]
    container = {}
    for k in reduce(lambda x,y:x+y,[template[secName].keys() for secName in dataSections]+[template[u'SPALTENBESCHRIFTUNG']],[]):
        container[k] = []
    return container

def readSingleFile(b, pixelName):
    d = unicode(b, 'cp1252')
    ll = d.splitlines()
    root = makeRoot(pixelName, ll)
    dataSections=[]
    section = root
    secId = 'root'
    for l in ll:
        if l.startswith('[') and l.endswith(']'):
            section, secId = LINE_HANDLER[u'Section'](root, dataSections, l[1:-1])
        else:
            LINE_HANDLER[secId](section, l)
    root[u'MESSDATEN'] = numpy.array(root[u'MESSDATEN'])
    return (root, dataSections)


class OscLoader(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Data Loader"

    _params=[("filename", u"Filename", "", Connectors.SUBTYPE_FILE)]

    @Worker.plug(Connectors.TYPE_ARRAY)
    def loadOsc(self, subscriber=0):
        result = loadOscFromFile(self.paramFilename.value, subscriber)
        result.seal()
        return result

