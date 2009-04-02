# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
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
__version__ = "Pyphant Sprint - opticalSkinModel"
# $Source$

import os, os.path, pkg_resources
LOGDIR = os.path.expanduser(u'~')
import logging
if LOGDIR==u'~':
    LOGDIR = os.getcwdu()
#    logging.basicConfig(level=logging.DEBUG)
#else:
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.join(LOGDIR, u'pyphant.log'),
                    filemode='w',
                    format="%(asctime)s - %(levelname)s:%(name)s:%(thread)d:%(module)s.%(funcName)s(l %(lineno)d):%(message)s")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)

import sys
def excepthook(type,value,traceback):
    log = logging.getLogger('pyphant')
    log.debug(u"An unhandled exception occured.",
              exc_info=(type,value,traceback))
    sys.__excepthook__(type,value,traceback)
sys.excepthook=excepthook
import wx
import sogl
import pyphant.wxgui2.paramvisualization.ParamVisReg as ParamVisReg
import pyphant.core.PyTablesPersister
import WorkerRepository
import ConfigureFrame
import platform
pltform = platform.system()

class wxPyphantApplication(wx.PySimpleApp):
    def __init__(self,pathToRecipe=None):
        self.pathToRecipe = pathToRecipe
        wx.PySimpleApp.__init__(self)

    def OnInit(self):
        if not wx.PySimpleApp.OnInit(self):
            return False
        self._logger=logging.getLogger("pyphant")
        sogl.SOGLInitialize()
        self._paramVisReg=ParamVisReg.ParamVisReg()
        self._frame = wxPyphantFrame(self)
        self._frame.Show()
        return True

    def getMainFrame(self):
        return self._frame

    def configureWorker(self, worker):
        configureFrame=ConfigureFrame.ConfigureFrame(self._frame, self._paramVisReg,  worker)
        if configureFrame.ShowModal() == wx.ID_OK:
            configureFrame.applyAll()

    def editCompositeWorker(self, worker):
        self._frame.editCompositeWorker(worker)


class wxPyphantFrame(wx.Frame):

    ID_WINDOW_TOP=100
    ID_WINDOW_LEFT=101
    ID_WINDOW_RIGHT=102
    ID_WINDOW_BOTTOM=103
    ID_CLOSE_COMPOSITE_WORKER = wx.NewId()
    ID_UPDATE_PYPHANT = wx.NewId()

    def __init__(self, _wxPyphantApp):
        wx.Frame.__init__(self, None, -1, "wxPyphant %s" % __version__, size=(640,480))
        import PyphantCanvas
        self._statusBar=self.CreateStatusBar()
        self._wxPyphantApp=_wxPyphantApp
        self._initMenuBar()
        self._initSash()
        self.recipeState=None
        self.onOpenCompositeWorker(None)
        self._workerRepository.Bind(wx.EVT_SASH_DRAGGED_RANGE,
                                    self.onFoldPanelBarDrag,
                                    id=self.ID_WINDOW_TOP,
                                    id2=self.ID_WINDOW_BOTTOM)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.compositeWorkerStack=[]
        wx.MessageBox("Located log directory at %s.\n"
                      "Logging will go to %s/pyphant.log." %
                      (LOGDIR,LOGDIR),
                      "Logging info")

    def _initSash(self):
        self._workerRepository = wx.SashLayoutWindow(self,
                                                     self.ID_WINDOW_RIGHT,
                                                     wx.DefaultPosition,
                                                     wx.Size(200,1000),
                                                     wx.NO_BORDER |wx.SW_3D
                                                     | wx.CLIP_CHILDREN)
        self._workerRepository.SetDefaultSize(wx.Size(220,1000))
        self._workerRepository.SetOrientation(wx.LAYOUT_VERTICAL)
        self._workerRepository.SetAlignment(wx.LAYOUT_RIGHT)
        self._workerRepository.SetSashVisible(wx.SASH_LEFT, True)
        self._workerRepository.SetExtraBorderSize(10)
        WorkerRepository.WorkerRepository(self._workerRepository)

    def onSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self,self._remainingSpace)
        event.Skip()

    def onFoldPanelBarDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return
        if event.GetId() == self.ID_WINDOW_RIGHT:
            self._workerRepository.SetDefaultSize(wx.Size(event.GetDragRect().width, 1000))
        # Leaves bits of itself behind sometimes
        wx.LayoutAlgorithm().LayoutWindow(self, self._remainingSpace)
        self._remainingSpace.Refresh()
        event.Skip()

    def onOpenCompositeWorker(self, event):
        if not self._wxPyphantApp.pathToRecipe:
            if pltform == 'Linux' or pltform == 'Darwin':
                osMessage = "Choose an existing recipe or cancel to create a new recipe"
            elif pltform=='Windows':
                osMessage = "Choose existing recipe to open or name a new recipe to create"
            else:
                raise OSError, "Operating System %s not supported!" % pltform
            wc = "Pyphant Recipe(*.h5)|*.h5"
            dlg = wx.FileDialog( self, message=osMessage, defaultDir=os.getcwd(),
                                 defaultFile="", wildcard=wc, style=wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self._wxPyphantApp.pathToRecipe = dlg.GetPath()
            else:
                dlg.Destroy()
                dlg = wx.FileDialog( self, message='Create a new recipe', defaultDir=os.getcwd(),
                                     defaultFile="", wildcard=wc, style=wx.SAVE)
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    if not path[:-3]=='.h5':
                        path+='.h5'
                    self._wxPyphantApp.pathToRecipe = path
            dlg.Destroy()

        import PyphantCanvas
        try:
            if self._wxPyphantApp.pathToRecipe[-3:] == '.h5':
                recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(self._wxPyphantApp.pathToRecipe)
            else:
                raise IOError("Unknown file format in file \""+self._wxPyphantApp.pathToRecipe+"\"")
            self._remainingSpace=PyphantCanvas.PyphantCanvas(self, recipe)
        except IOError, error:
            self._remainingSpace=PyphantCanvas.PyphantCanvas(self)
        self.recipeState='clean'
        self._remainingSpace.diagram.recipe.registerListener(self.recipeChanged)

    def recipeChanged(self, event):
        self.recipeState='dirty'

    def onSaveCompositeWorker(self, event=None):
        pyphant.core.PyTablesPersister.saveRecipeToHDF5File(self._remainingSpace.diagram.recipe,
                                                            self._wxPyphantApp.pathToRecipe)
        self.recipeState='clean'

    def _initMenuBar(self):
        self._menuBar = wx.MenuBar()
        self._fileMenu = wx.Menu()
        #self._fileMenu.Append( wx.ID_NEW, "&New\tCTRL+n")
        #self._fileMenu.Append( wx.ID_OPEN, "&Open\tCTRL+o")
        self._fileMenu.Append( wx.ID_SAVE, "&Save\tCTRL+s")
        self._fileMenu.Append( wx.ID_EXIT, "E&xit" )
        self._menuBar.Append( self._fileMenu, "&File" )
        self._closeCompositeWorker = wx.Menu()
        self._closeCompositeWorker.Append(self.ID_CLOSE_COMPOSITE_WORKER, "&Close Composite Worker")
        self._menuBar.Append( self._closeCompositeWorker, "&Close Composite Worker")
        self._updateMenu = self.createUpdateMenu()
        self._menuBar.Append( self._updateMenu, "&Update")
        self.SetMenuBar( self._menuBar )
        self._menuBar.EnableTop(1, False)
        #self.Bind(wx.EVT_MENU, self.onCreateNew, id=wx.ID_NEW)
        #self.Bind(wx.EVT_MENU, self.onOpenCompositeWorker, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onSaveCompositeWorker, id=wx.ID_SAVE)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onCloseCompositeWorker, id=self.ID_CLOSE_COMPOSITE_WORKER)

    def createUpdateMenu(self):
        updateMenu = wx.Menu()
        updateMenu.Append( self.ID_UPDATE_PYPHANT, "Update &Pyphant" )
        self.Bind(wx.EVT_MENU, self.onUpdatePyphant, id=self.ID_UPDATE_PYPHANT)
        self.updateIds = { self.ID_UPDATE_PYPHANT : 'pyphant' }
        for toolbox in pkg_resources.iter_entry_points("pyphant.workers"):
            dist = toolbox.dist
            nId = wx.NewId()
            self.updateIds[nId] = dist.key
            updateMenu.Append( nId, "Update %s (%s)" % (dist.project_name, dist.version) )
            self.Bind(wx.EVT_MENU, self.onUpdatePyphant, id=nId)
        return updateMenu


    def onUpdatePyphant(self, event):
        import pyphant.core.UpdateManager
        pyphant.core.UpdateManager.updatePackage(self.updateIds[event.Id])

    def onQuit(self,event):
        self.Close()

    def onClose(self, event):
        dlgid=None
        if self.recipeState!='clean':
            cpt = "Save changed recipe?"
            msg = "The recipe has changed since the last saving.\nDo you want to save before terminating?"
            dlg = wx.MessageDialog(self, msg, cpt, style=wx.YES|wx.NO|wx.CANCEL|wx.ICON_QUESTION)
            dlgid = dlg.ShowModal()
            if dlgid == wx.ID_YES:
                self.onSaveCompositeWorker()
            dlg.Destroy()
        if dlgid != wx.ID_CANCEL:
            self.Destroy()

    def editCompositeWorker(self, worker):
        import PyphantCanvas
        self.compositeWorkerStack.append(self._remainingSpace)
        self._remainingSpace=PyphantCanvas.PyphantCanvas(self, worker)
        self._remainingSpace.diagram.recipe.registerListener(self.recipeChanged)
        self._menuBar.EnableTop(1, True)

    def onCloseCompositeWorker(self, event):
        self._remainingSpace.Destroy()
        self._remainingSpace=self.compositeWorkerStack.pop()
        if len(self.compositeWorkerStack)==0:
            self._menuBar.EnableTop(1, False)


import optparse

def startWxPyphant():
    usage = "usage: %prog [options] pathToRecipe"
    parser = optparse.OptionParser(usage,version=__id__.replace('$',''))
    (options, args) = parser.parse_args()

    if len(args)>0:
        pathToRecipe = args[0]
    else:
        pathToRecipe = None
    wxPyphantApp = wxPyphantApplication(pathToRecipe)
    wxPyphantApp.MainLoop()
