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

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import pylab
import pyphant.core.Connectors
from pyphant.core import DataContainer
from pyphant.wxgui2.DataVisReg import DataVisReg
from pyphant.quantities.PhysicalQuantities import isQuantity
from pyphant.visualizers.Chart import LineChart

class AbsorptionVisualizer(LineChart):
    name='OSC Visualizer'


    def prepare(self):
        def setField(name):
            self.xData = data[name].dimensions[0]
            self.yData = data[name]
            pylab.xlabel(data[name].dimensions[0].label)
            pylab.ylabel(data[name].label)

        pylab.ioff()
        pylab.figure()

        data = self.dataContainer
        if self.dataContainer.numberOfColumns()>2:
            if u'Smoothed Absorption' in data.longnames.keys():
                setField(u'Smoothed Absorption')
            elif u'Absorption' in data.longnames.keys():
                setField(u'Absorption')
            else:
                self.xData = data[u'Wellenlänge[nm]']
                self.yData = data[u'ScopRaw[counts]']
                pylab.ylabel('Scop Raw / a.u.')
        else:
            self.xData = self.dataContainer[0]
            self.yData = self.dataContainer[1]
        for i in xrange(len(self.xData.data)):
            self.ordinates.append(self.yData.data[i])
            self.abscissae.append(self.xData.data[i])
        if u'Minima' in data.longnames.keys():
            mins = data[u'Minima']
            for i in xrange(len(mins.data)):
                self.mins.append(mins.data[i])

        pylab.xlabel('Wavelength $\lambda$ / nm')
        pylab.title(self.dataContainer.longname)

    def draw(self):
        for i in xrange(len(self.ordinates)):
            pylab.plot(self.abscissae[i],self.ordinates[i])
        for i in xrange(len(self.mins)):
            pylab.axvline(self.mins[i])

DataVisReg.getInstance().registerVisualizer(pyphant.core.Connectors.TYPE_ARRAY, AbsorptionVisualizer)
















