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


from pyphant.core import (Connectors, DataContainer)
from pyphant.wxgui2.DataVisReg import DataVisReg
import os
import wx
import csv

from scipy.io import write_array
from pyphant.quantities import isQuantity
import scipy

class ExternalDAT(object):
    name='Export to ASCII file'
    def __init__(self, dataContainer):
        self.dataContainer = dataContainer
        self.execute()

    def execute(self):
        dialog = wx.FileDialog(None,message='Choose file for saving the data', defaultDir=os.getcwd(),
                              style=wx.SAVE | wx.OVERWRITE_PROMPT,
                               wildcard = "Comma separated values (*.csv)|*.csv|Plain text (*.dat)|*.dat")
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            print "Selected:",path
        else:
            print "Nothing was selected."
        dialog.Destroy()
        hash, uriType = DataContainer.parseId(self.dataContainer.id)
        if uriType == u"field":
            self.saveField(path)
        elif uriType == u"sample":
            self.saveSample(path)

    def saveField(self, path):
        if not isQuantity(self.dataContainer.unit):
            self.ordinate = self.dataContainer.data*self.dataContainer.unit
        else:
            self.ordinate = self.dataContainer.data*self.dataContainer.unit.value
        self.abscissa = self.dataContainer.dimensions[0].data
        outData = scipy.transpose(scipy.array([self.abscissa,self.ordinate]))
        if path[-3:] == 'csv':
            outFile = file(path,'wb')
            csvWriter = csv.writer(outFile,dialect='excel')
            csvWriter.writerow([self.dataContainer.dimensions[0].label, self.dataContainer.label])
            csvWriter.writerows(outData.tolist())
        else:
            outFile = file(path,'w')
            outFile.write(str([self.dataContainer.dimensions[0].label, self.dataContainer.label])+"\n")
            write_array(outFile,outData)
        outFile.close()

    def saveSample(self, path):
        outData = self.dataContainer.data

        if path[-3:] == 'csv':
            outFile = file(path,'wb')
            csvWriter = csv.writer(outFile,dialect='excel')
            #csvWriter.writerow([self.dataContainer.dimensions[0].label, self.dataContainer.label])
            csvWriter.writerows(outData.tolist())
        else:
            outFile = file(path,'w')
            #outFile.write(str([self.dataContainer.dimensions[0].label, self.dataContainer.label])+"\n")
            write_array(outFile,outData.tolist())
        outFile.close()


DataVisReg.getInstance().registerVisualizer(Connectors.TYPE_ARRAY, ExternalDAT)














