# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
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

enc=lambda s: unicode(s, "utf-8")

import platform,os,socket,datetime
import fmfgen, numpy
import pyphant.core.Helpers

def dtype2colFormat(dtype):
    if dtype.name.startswith('float'):
        return "%e"
    elif dtype.name.startswith('int'):
        return "%i"
    else:
        print dtype
        return "%s"

def field2fmf(fieldContainer):
    factory = fmfgen.gen_factory(out_coding='utf-8', eol='\n')
    fc = factory.gen_fmf()
    fc.add_reference_item('author', pyphant.core.Helpers.getUsername())
    fc.add_reference_item('title',fieldContainer.longname)
    fc.add_reference_item('place',socket.getfqdn())
    fc.add_reference_item('created',datetime.datetime.utcnow().isoformat())
    sec = factory.gen_section("parameters")
    for key,value in fieldContainer.attributes.iteritems():
        if type(value)==type([]):
            output = ' '.join(value)
        else:
            output = str(value)
        sec.add_item(key,output)
    fc.add_section(sec)
    if len(fieldContainer.data.shape)==1:
        dim = fieldContainer.dimensions[0]
        if fieldContainer.error == None:
            data = numpy.vstack([dim.data, fieldContainer.data])
        else:
            data = numpy.vstack([dim.data, fieldContainer.data,fieldContainer.error])
        tab = factory.gen_table(data.transpose())
        tab.add_column_def(dim.longname, dim.shortname, str(dim.unit))
        if fieldContainer.error == None:
            errorSymbol = None
        else:
            errorSymbol = u"\\Delta_{%s}" % fieldContainer.shortname
        tab.add_column_def(fieldContainer.longname,
                           fieldContainer.shortname,
                           str(fieldContainer.unit),
                           dependencies = [dim.shortname],
                           error = errorSymbol)
        if fieldContainer.error != None:
            tab.add_column_def(u"uncertainty of %s" % fieldContainer.longname,
                               errorSymbol,
                               str(fieldContainer.unit))
    elif fieldContainer.dimensions[0].isIndex():
        dim = fieldContainer.dimensions[-1]
        try:
            data = numpy.vstack([dim.data, fieldContainer.data])
        except:
            print dim.data,fieldContainer
        tab = factory.gen_table(data.transpose())
        tab.add_column_def(dim.longname, dim.shortname, str(dim.unit), format=dtype2colFormat(dim.data.dtype))
        superscript = ('st','nd','rd')
        for i in xrange(len(fieldContainer.dimensions[0].data)):
            if i<3:
                sup = superscript[i]
            else:
                sup = 'th'
            longname = "%i$^%s$ %s" % (i+1,sup,fieldContainer.longname)
            shortname = "%s_%i" % (fieldContainer.shortname,i+1)
            tab.add_column_def(longname,shortname,
                               str(fieldContainer.unit),
                               dependencies = [dim.shortname],
                               format=dtype2colFormat(fieldContainer.data.dtype))
    fc.add_table(tab)
    return str(fc)

import wx
ID_EXIT = 102

class FMFframe(wx.Frame):
    def __init__(self,parent, ID, title):
        wx.Frame.__init__(self,parent,ID, title,
                          wx.DefaultPosition,wx.Size(300,300))
        self.CreateStatusBar()
        self.SetStatusText("Full-Metadata Format")
        p = wx.Panel(self)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(101, "&About",
                    "Full-Metadata Format Viewer")
        menu.AppendSeparator()
        menu.Append(ID_EXIT,"E&xit","Terminate the program")
        menuBar.Append(menu,"&File")
        self.SetMenuBar(menuBar)

        wx.EVT_MENU(self,ID_EXIT, self.timeToQuit)

    def timeToQuit(self,event):
        self.Close(True)

class TextFrame(wx.Frame):
    def __init__(self,fmf):
        wx.Frame.__init__(self,None,-1,'FMFWriter', size=(300,200))
        multiText = wx.TextCtrl(self,-1,fmf,size=(200,200),style=wx.TE_MULTILINE)
        multiText.SetInsertionPoint(0)

class MyApp(wx.App):
    def OnInit(self):
        frame = FMFframe(None,-1,"Pyphant Full-Metadata Format Viewer")
        frame.Show(True)
        return True

    def OnExit(self):
        self.ExitMainLoop()
        wx.Exit()

class FMFWriter(object):
    name='FMF Writer'
    def __init__(self, fieldContainer,show=True):
        self.fieldContainer = fieldContainer
        self.show = show
        self.execute()

    def execute(self):
        self.text =  field2fmf(self.fieldContainer)
        app = wx.PySimpleApp()
        frame = TextFrame(self.text)
        frame.Show()
        app.MainLoop()

    def OnExit(self):
        self.ExitMainLoop()
        wx.Exit()
