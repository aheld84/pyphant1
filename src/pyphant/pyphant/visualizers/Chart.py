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

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import copy
import pylab
import numpy
import pyphant.core.Connectors
from pyphant.core import DataContainer
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.quantities import isQuantity

class Chart(object):
    name='General chart'
    def __init__(self, dataContainer,show=True):
        self.dataContainer = dataContainer
        self.data = []
        self.prepare()
        for d in self.data:
            self.draw(**d)
        if show:
            self.finalize()

    def draw(self, **kwargs):
        pass

    def prepare(self):
        pylab.ioff()
        self.figure = pylab.figure()
        if isinstance(self.dataContainer.data[0], DataContainer.FieldContainer):
            ref = self.dataContainer.data[0]
            self.addDataContainer(ref)
            for fc in self.dataContainer.data[1:]:
                fc = fc.inUnitsOf(ref)
                fc.dimensions[-1] = fc.dimensions[-1].inUnitsOf(ref.dimensions[-1])
                self.addDataContainer(fc)
            pylab.xlabel(self.dataContainer.data[0].dimensions[-1].shortlabel)
            pylab.ylabel(self.dataContainer.data[0].label)
        else:
            self.addDataContainer(self.dataContainer)
            pylab.xlabel(self.dataContainer.dimensions[-1].shortlabel)
            pylab.ylabel(self.dataContainer.label)
        try:
            pylab.title(self.dataContainer.attributes['title'])
        except KeyError,TypeError:
            pass
        self.xmin = min([numpy.nanmin(d['abscissa']) for d in self.data])
        self.xmax = max([numpy.nanmax(d['abscissa']) for d in self.data])
        self.ymin = min([numpy.nanmin(d['data']) for d in self.data])
        self.ymax = max([numpy.nanmax(d['data']) for d in self.data])

    def addDataContainer(self, dataContainer):
        dataDict = {}
        if len(dataContainer.data.shape)==1:
            dataDict['data'] = dataContainer.data[numpy.newaxis,:]
            if dataContainer.error != None:
                dataDict['error'] = dataContainer.error[numpy.newaxis,:]
            else:
                dataDict['error'] = None
            if dataContainer.mask != None:
                dataDict['mask'] = dataContainer.mask[numpy.newaxis,:]
                dataDict['maskedData'] = numpy.ma.array(dataDict['data'], mask=dataDict['mask'])
            else:
                dataDict['mask'] = None
                dataDict['maskedData'] = numpy.ma.array(dataDict['data'])
        else:
            dataDict['data'] = dataContainer.data
            dataDict['error'] = dataContainer.error
            dataDict['mask'] = dataContainer.mask
            if dataDict['mask'] != None:
                dataDict['maskedData'] = numpy.ma.array(dataDict['data'], mask=dataDict['mask'])
            else:
                dataDict['maskedData'] = numpy.ma.array(dataDict['data'])
        dataDict['abscissa'] = dataContainer.dimensions[-1].data
        self.data.append(dataDict)


    def finalize(self):
        pylab.ion()
        pylab.show()


class BarChart(Chart):
    name = u"Bar chart"

    def draw(self, abscissa, data, maskedData, error, **kwargs):
        width = numpy.min(numpy.diff(abscissa))
        ymin = 0
        if self.ymin < ymin:
            ymin = self.ymin * 1.03
        if error == None:
            for ordinate in maskedData:
                pylab.bar(abscissa, ordinate, capsize=0,
                          width=width)
        else:
            for i in xrange(data.shape[0]):
                line = pylab.bar(abscissa, maskedData[i],
                                 yerr=error[i],
                                 width=width)
        xextent = (self.xmax-self.xmin)*0.03
        pylab.axis([self.xmin-xextent, self.xmax+width+xextent, ymin, self.ymax*1.03])


class LineChart(Chart):
    name = u"Line chart"
    linestyle = '-'

    def draw(self, abscissa, data, maskedData, error, **kwargs):
        if error == None:
            for ordinate in maskedData:
                pylab.plot(abscissa, ordinate, self.linestyle)
        else:
            for i in xrange(data.shape[0]):
                line = pylab.plot(abscissa, maskedData[i], self.linestyle)
                color = [l._color for l in line]
                for direction in [-1.,1.]:
                    ordinate = maskedData[i] + direction*error[i]
                    line = pylab.plot(abscissa, ordinate, linestyle=':')
                    for j in xrange(len(color)):
                        line[j]._color = color[j]
        pylab.axis([self.xmin, self.xmax, self.ymin, self.ymax])

class ScatterPlot(LineChart):
    name = u"Scatter Plot"
    linestyle = 'o'


DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, BarChart)
DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, LineChart)
DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, ScatterPlot)

