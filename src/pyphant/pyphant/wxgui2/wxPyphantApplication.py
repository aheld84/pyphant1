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
__version__ = "Sprint"
# $Source$

import os, os.path, pkg_resources
from pyphant.core.Helpers import getPyphantPath
LOGDIR = getPyphantPath()[:-1]
import logging
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
import wx
import sogl
import pyphant.wxgui2.paramvisualization.ParamVisReg as ParamVisReg
import pyphant.core.PyTablesPersister
import WorkerRepository
import ConfigureFrame
import platform
from pyphant.core.KnowledgeNode import (KnowledgeNode, KnowledgeManager)
import webbrowser
pltform = platform.system()

class wxPyphantApplication(wx.PySimpleApp):
    def __init__(self, pathToRecipe=None):
        self.pathToRecipe = pathToRecipe
        wx.PySimpleApp.__init__(self)

    def OnInit(self):
        if not wx.PySimpleApp.OnInit(self):
            return False
        self._logger=logging.getLogger("pyphant")
        self._excframe = wx.Frame(None, -2, "")
        sys.excepthook = self.excepthook
        sogl.SOGLInitialize()
        self._knowledgeNode = None
        self._paramVisReg=ParamVisReg.ParamVisReg()
        self._frame = wxPyphantFrame(self)
        self._frame.Show()
        return True

    def excepthook(self, type, value, trace):
        self._logger.debug(u"An unhandled exception occured.",
                           exc_info=(type, value, trace))
        sys.__excepthook__(type, value, trace)
        try:
            cpt = type.__name__
            #import traceback
            #traceStr = ''.join(traceback.format_exception(type, value, trace))
            msg = "Additional information:\n%s\n\n" % value
            dlg = wx.MessageDialog(self._excframe, msg, cpt, wx.OK)
            dlg.ShowModal()
        except:
            # avoid loop if displaying error message fails
            self._logger.debug(u"Failed to display error message in wxPyphant.")

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
        if self._wxPyphantApp.pathToRecipe[-3:] == '.h5':
            if os.path.exists(self._wxPyphantApp.pathToRecipe):
                recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(self._wxPyphantApp.pathToRecipe)
                #from pyphant.core import KnowledgeManager
                #KnowledgeManager.KnowledgeManager.getInstance().registerURL(
                #    "file:///"+os.path.realpath(self._wxPyphantApp.pathToRecipe)
                 #   )
                self._remainingSpace=PyphantCanvas.PyphantCanvas(self, recipe)
            else:
                self._remainingSpace=PyphantCanvas.PyphantCanvas(self)
        else:
            raise IOError("Unknown file format in file \""+self._wxPyphantApp.pathToRecipe+"\"")
        self.recipeState='clean'
        self._remainingSpace.diagram.recipe.registerListener(self.recipeChanged)

    def recipeChanged(self, event):
        self.recipeState='dirty'

    def onSaveCompositeWorker(self, event=None):
        pyphant.core.PyTablesPersister.saveRecipeToHDF5File(
            self._remainingSpace.diagram.recipe,
            self._wxPyphantApp.pathToRecipe,
            self._fileMenu.IsChecked(wx.ID_FILE4))
        self.recipeState='clean'

    def onSaveAsCompositeWorker(self, event=None):
        msg = "Select file to save recipe."
        wc = "Pyphant recipe (*.h5)|*.h5"
        dlg = wx.FileDialog(self, message = msg, defaultDir = os.getcwd(),
                            defaultFile = "", wildcard = wc, style = wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not filename.endswith(".h5"):
                filename += ".h5"
            pyphant.core.PyTablesPersister.saveRecipeToHDF5File(
                self._remainingSpace.diagram.recipe,
                filename,
                self._fileMenu.IsChecked(wx.ID_FILE4))
            self._wxPyphantApp.pathToRecipe = filename
            self.recipeState='clean'
        else:
            dlg.Destroy()

    def _initMenuBar(self):
        self._menuBar = wx.MenuBar()
        self._fileMenu = wx.Menu()
        #self._fileMenu.Append( wx.ID_NEW, "&New\tCTRL+n")
        #self._fileMenu.Append( wx.ID_OPEN, "&Open\tCTRL+o")
        self._fileMenu.AppendCheckItem(wx.ID_FILE4, "Save &results\tCTRL+r")
        self._fileMenu.Check(wx.ID_FILE4, True)
        self._fileMenu.Append( wx.ID_SAVE, "&Save\tCTRL+s")
        self._fileMenu.Append( wx.ID_SAVEAS, "Save &as\tCTRL+a")
        self._fileMenu.Append( wx.ID_EXIT, "E&xit" )
        self._fileMenu.Append( wx.ID_FILE1, "Import HDF5 or FMF from &URL" )
        self._fileMenu.Append( wx.ID_FILE2, "&Import local HDF5 or FMF file")
        self._fileMenu.Append( wx.ID_FILE3, "Start/pause sharing &knowledge")
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
        self.Bind(wx.EVT_MENU, self.onSaveAsCompositeWorker, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onCloseCompositeWorker, id=self.ID_CLOSE_COMPOSITE_WORKER)
        self.Bind(wx.EVT_MENU, self.onImportURL, id=wx.ID_FILE1)
        self.Bind(wx.EVT_MENU, self.onImportLocal, id=wx.ID_FILE2)
        self.Bind(wx.EVT_MENU, self.onShare, id=wx.ID_FILE3)

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
            try:
                self._wxPyphantApp._knowledgeNode.stop()
            except AttributeError:
                pass
            self._wxPyphantApp._excframe.Destroy()
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

    def onImportURL(self, event):
        cpt = "Import HDF5 or FMF from URL"
        msg = "Enter an URL to a valid HDF5 or FMF file \
(e.g. http://www.example.org/data.h5).\n\
The file is stored permanently in your home directory in the \
.pyphant directory\nand all DataContainers contained in that file are \
available by using the\nEmd5Src Worker even after restarting wxPyphant.\n\
HTTP redirects are resolved automatically, i.e. DOIs are supported as well."
        dlg = wx.TextEntryDialog(self, msg, cpt)
        dlgid = dlg.ShowModal()
        if dlgid != wx.ID_CANCEL:
            url = dlg.GetValue()
            cpt2 = "Info"
            msg2 = "Successfully imported DataContainers from\n'%s'"\
                   % (url ,)
            km = KnowledgeManager.getInstance()
            try:
                km.registerURL(url)
            except Exception:
                cpt2 = "Error"
                msg2 = "'%s' is not a valid URL to a HDF5 or FMF file."\
                       % (url, )
            finally:
                dlg2 = wx.MessageDialog(self, msg2, cpt2, wx.OK)
                dlgid2 = dlg2.ShowModal()

    def onImportLocal(self, event):
        msg = "Select HDF5 or FMF file to import DataContainer(s) from."
        wc = "*.h5, *.hdf, *.hdf5, *.fmf|*.h5;*.hdf;*.hdf5;*.fmf"
        dlg = wx.FileDialog(self, message = msg, defaultDir = os.getcwd(),
                            defaultFile = "", wildcard = wc, style = wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            url = 'file://' + os.path.realpath(filename)
            km = KnowledgeManager.getInstance()
            cpt2 = "Info"
            msg2 = "Successfully imported DataContainer(s) from\n'%s'"\
                   % (filename ,)
            try:
                km.registerURL(url)
            except Exception:
                cpt2 = "Error"
                msg2 = "'%s' is not a valid HDF5 or FMF file.\n\
(Tried to import from '%s')" % (filename, url)
            finally:
                dlg2 = wx.MessageDialog(self, msg2, cpt2, wx.OK)
                dlgid2 = dlg2.ShowModal()
        else:
            dlg.Destroy()

    def onShare(self, event):
        cpt = "Share Knowledge"
        msg = ""
        if self._wxPyphantApp._knowledgeNode is None:
            try:
                logg = self._wxPyphantApp._logger
                from pyphant.core.KnowledgeNode import get_kn_autoport
                ports = [8080] + range(48621, 48771)
                self._wxPyphantApp._knowledgeNode = get_kn_autoport(
                    ports, logg, start=True, web_interface=True)
                url = self._wxPyphantApp._knowledgeNode.url
                msg += "Knowledge node is listening @ %s.\n"\
                       "Sharing is experimental and therefore restric"\
                       "ted\nto the loopback interface." % url
                webbrowser.open_new(url)
            except Exception, exep:
                msg += "Could not start web server."
                from socket import error as socket_error
                if isinstance(exep, socket_error):
                    try:
                        #Python 2.6
                        eno = err.errno
                    except AttributeError:
                        #Python 2.5
                        eno = err.args[0]
                    from errno import EADDRINUSE
                    if eno == EADDRINUSE:
                        msg += "\nReason: Could not find a free port."\
                               "\n(You may stop other applications or "\
                               "wait for the OS\nto free some ports.)"
        elif not self._wxPyphantApp._knowledgeNode.app.serve:
            msg += "Resumed sharing."
            self._wxPyphantApp._knowledgeNode.app.serve = True
        else:
            self._wxPyphantApp._knowledgeNode.app.serve = False
            msg += "Disabled sharing."
        dlg = wx.MessageDialog(self, msg, cpt, wx.OK)
        dlg.ShowModal()


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
