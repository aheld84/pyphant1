# -*- coding: utf-8 -*-

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
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import copy
import pylab
import numpy
import pyphant.core.Connectors
from pyphant.core import DataContainer
from pyphant.wxgui2.DataVisReg import DataVisReg
from Scientific.Physics.PhysicalQuantities import isPhysicalQuantity

class Chart(object):
    name='General chart'
    def __init__(self, dataContainer,show=True):
        self.dataContainer = dataContainer
        self.mins = []
        self.prepare()
        self.draw()
        if show:
            self.finalize()

    def draw(self):
        pass
    
    def prepare(self):
        pylab.ioff()
        self.figure = pylab.figure()
        if len(self.dataContainer.data.shape)==1:
            self.data = self.dataContainer.data[numpy.newaxis,:]
            if self.dataContainer.error != None:
                self.error = self.dataContainer.error[numpy.newaxis,:]
            else:
                self.error = None
            if self.dataContainer.mask != None:
                self.mask = self.dataContainer.mask[numpy.newaxis,:]
                self.maskedData = numpy.ma.array(self.data, mask=self.mask)
            else:
                self.mask = None
                self.maskedData = numpy.ma.array(self.data)
        else:
            self.data = self.dataContainer.data
            self.error = self.dataContainer.error
            self.mask = self.dataContainer.mask
            if self.mask != None:
                self.maskedData = numpy.ma.array(self.data, mask=self.mask)
            else:
                self.maskedData = numpy.ma.array(self.data)
        self.abscissa = self.dataContainer.dimensions[-1].data
        pylab.xlabel(self.dataContainer.dimensions[-1].shortlabel)
        pylab.ylabel(self.dataContainer.label)
        try:
            pylab.title(self.dataContainer.attributes['title'])
        except KeyError,TypeError:
            pass
        self.xmin=numpy.nanmin(self.abscissa)
        self.xmax=numpy.nanmax(self.abscissa)
        self.ymin=numpy.nanmin(self.data)
        self.ymax=numpy.nanmax(self.data)
        
    def finalize(self):
        pylab.ion()
        pylab.show()


#class BarChart(Chart):
#    name = u"Bar chart"
#    def draw(self):
#        # xerr and yerr added due to error in matplotlib 0.87.4
#        self.error = pylab.zeros(len(self.abscissae[0]))
#        for i in xrange(len(self.ordinates)):
#            pylab.bar(self.abscissae[i],self.ordinates[i],
#                      xerr = self.error,yerr = self.error,
#                      capsize=0,
#                      width=pylab.min(pylab.diff(self.abscissae[i])))
        

class LineChart(Chart):
    name = u"Line chart"
    linestyle = '-'
    def draw(self):
        if self.error == None:
            for ordinate in self.maskedData:
                pylab.plot(self.abscissa, ordinate, self.linestyle)
        else:
            for i in xrange(self.data.shape[0]):
                line = pylab.plot(self.abscissa, self.maskedData[i], self.linestyle)
                color = [l._color for l in line]
                for direction in [-1.,1.]:
                    ordinate = self.maskedData[i] + direction*self.error[i]
                    line = pylab.plot(self.abscissa, ordinate, linestyle=':')
                    for j in xrange(len(color)):
                        line[j]._color = color[j]
        for i in xrange(len(self.mins)):
            pylab.axvline(self.mins[i])
        pylab.axis([self.xmin, self.xmax, self.ymin, self.ymax])

class ScatterPlot(LineChart):
    name = u"Scatter Plot"
    linestyle = 'o'


#DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, BarChart)
DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, LineChart)
DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_IMAGE, ScatterPlot)















