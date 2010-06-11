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
LOGDIR = getPyphantPath()
import logging
import logging.handlers
#    logging.basicConfig(level=logging.DEBUG)
#else:
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.join(LOGDIR, u'pyphant.log'),
                    filemode='w',
                    format="%(asctime)s - %(levelname)s:%(name)s:%(thread)"\
                    "d:%(module)s.%(funcName)s(l %(lineno)d):%(message)s")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logbuffer = logging.handlers.MemoryHandler(1000)
logging.getLogger('').addHandler(console)
logging.getLogger('').addHandler(logbuffer)

import sys
import wx
import wx.aui
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
        self._logger = logging.getLogger("pyphant")
        sys.excepthook = self.excepthook
        sogl.SOGLInitialize()
        self._knowledgeNode = None
        self._paramVisReg = ParamVisReg.ParamVisReg()
        self._frame = wxPyphantFrame(self)
        self._frame.Show()
        return True

    def excepthook(self, type, value, trace):
        self._logger.debug(u"An unhandled exception occured.",
                           exc_info=(type, value, trace))
        sys.__excepthook__(type, value, trace)

    def getMainFrame(self):
        return self._frame

    def configureWorker(self, worker):
        configureFrame = ConfigureFrame.ConfigureFrame(self._frame,
                                                       self._paramVisReg,
                                                       worker)
        if configureFrame.ShowModal() == wx.ID_OK:
            configureFrame.applyAll()

    def editCompositeWorker(self, worker):
        self._frame.editCompositeWorker(worker)


class wxPyphantFrame(wx.Frame):

    ID_WINDOW_TOP = 100
    ID_WINDOW_LEFT = 101
    ID_WINDOW_RIGHT = 102
    ID_WINDOW_BOTTOM = 103
    ID_CLOSE_COMPOSITE_WORKER = wx.NewId()
    ID_UPDATE_PYPHANT = wx.NewId()
    ID_VIEW_WORKERREP = wx.NewId()
    ID_VIEW_LOGFILE = wx.NewId()
    ID_KM_URL = wx.NewId()
    ID_KM_LOCAL = wx.NewId()
    ID_KM_ZSTACK_XML = wx.NewId()
    ID_KM_SHARE = wx.NewId()

    def __init__(self, _wxPyphantApp):
        self.titleStr = "wxPyphant %s | Recipe: %s" % (__version__, "%s")
        wx.Frame.__init__(self, None, -1, self.titleStr % "None",
                          size=(640,480))
        import PyphantCanvas
        self._statusBar = self.CreateStatusBar()
        self._wxPyphantApp = _wxPyphantApp
        self._initMenuBar()
        self._initSash()
        self.recipeState = None
        self.onOpenCompositeWorker(None)
        self._initAui()
        self._workerRepository.Bind(wx.EVT_SASH_DRAGGED_RANGE,
                                    self.onFoldPanelBarDrag,
                                    id=self.ID_WINDOW_TOP,
                                    id2=self.ID_WINDOW_BOTTOM)
        #self.Bind(wx.EVT_SIZE, self.onSize)
        self.compositeWorkerStack = []

    def _initSash(self):
        self._workerRepository = wx.SashLayoutWindow(
            self, self.ID_WINDOW_RIGHT, wx.DefaultPosition, wx.Size(220,1000),
            wx.NO_BORDER)
        #self._workerRepository.SetDefaultSize(wx.Size(220,1000))
        #self._workerRepository.SetOrientation(wx.LAYOUT_VERTICAL)
        #self._workerRepository.SetAlignment(wx.LAYOUT_RIGHT)
        #self._workerRepository.SetSashVisible(wx.SASH_LEFT, True)
        #self._workerRepository.SetExtraBorderSize(10)
        try:
            WorkerRepository.WorkerRepository(self._workerRepository)
        except:
            import sys
            self._wxPyphantApp._logger.debug(u"An exception occured while "\
                                             "loading the toolboxes.",
                                             exc_info=sys.exc_info())
            wx.MessageBox("An error has occurred while importing "\
                          "the toolboxes.\nPlease investigate the logfile "\
                          "for further details.\nThe logfile is located at %s\n"\
                          "You may also try to update and restart wxPyphant."\
                          % os.path.join(LOGDIR, 'pyphant.log'),
                          "Toolbox Error!")
            self._workerRepository = wx.SashLayoutWindow(
                self, self.ID_WINDOW_RIGHT, wx.DefaultPosition,
                wx.Size(220,1000),
                wx.NO_BORDER)

    def _initAui(self):
        self._auiManager = wx.aui.AuiManager(self)
        class ClickableText(wx.TextCtrl):
            def __init__(self, *args, **kwargs):
                wx.TextCtrl.__init__(self, *args, **kwargs)
                self.Bind(wx.EVT_LEFT_DOWN,  self.OnClick)
            def OnClick(self, event):
                logbuffer.flush()
                event.Skip()
        self._logpane = ClickableText(self, -1, "",
                                      wx.DefaultPosition, wx.Size(640, 200),
                                      wx.NO_BORDER | wx.TE_MULTILINE \
                                      | wx.TE_READONLY)
        class WxHandler(logging.Handler):
            def __init__(self, ctrl):
                logging.Handler.__init__(self)
                self.ctrl = ctrl
            def emit(self, record):
                try:
                    self.ctrl.AppendText(self.format(record) + "\n")
                except wx.PyDeadObjectError:
                    pass
        handler = WxHandler(self._logpane)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s:%(name)s:%(thread)"\
            "d:%(module)s.%(funcName)s(l %(lineno)d):%(message)s"))
        logbuffer.setTarget(handler)
        logbuffer.flush()
        self._auiManager.AddPane(self._logpane, wx.BOTTOM, 'Logfile @ %s'\
                                 ' (click into text to update)' \
                                 % os.path.join(LOGDIR, 'pyphant.log'))
        self._auiManager.AddPane(self._workerRepository, wx.RIGHT,
                                 'Worker Repository')
        self._auiManager.AddPane(self._remainingSpace, wx.CENTER, 'Main')
        wrpane = self._auiManager.GetPane(self._workerRepository)
        wrpane.Floatable(False)
        wrpane.Movable(False)
        self._auiManager.Update()

    def onSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self,self._remainingSpace)
        event.Skip()

    def onFoldPanelBarDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return
        if event.GetId() == self.ID_WINDOW_RIGHT:
            self._workerRepository.SetDefaultSize(
                wx.Size(event.GetDragRect().width, 1000))
        # Leaves bits of itself behind sometimes
        #wx.LayoutAlgorithm().LayoutWindow(self, self._remainingSpace)
        self._remainingSpace.Refresh()
        event.Skip()

    def onOpenCompositeWorker(self, event):
        if not self._wxPyphantApp.pathToRecipe:
            if pltform == 'Linux' or pltform == 'Darwin':
                osMessage = "Choose an existing recipe or cancel to create "\
                            "a new recipe"
            elif pltform == 'Windows':
                osMessage = "Choose existing recipe to open or name a new "\
                            "recipe to create"
            else:
                raise OSError, "Operating System %s not supported!" % pltform
            wc = "Pyphant Recipe(*.h5)|*.h5"
            dlg = wx.FileDialog(self, message=osMessage, defaultDir=os.getcwd(),
                                defaultFile="", wildcard=wc, style=wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self._wxPyphantApp.pathToRecipe = dlg.GetPath()
            else:
                dlg.Destroy()
                dlg = wx.FileDialog(self, message='Create a new recipe',
                                    defaultDir=os.getcwd(), defaultFile="",
                                    wildcard=wc, style=wx.SAVE)
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    if not path[:-3] == '.h5':
                        path += '.h5'
                    self._wxPyphantApp.pathToRecipe = path
            dlg.Destroy()
        import PyphantCanvas
        if self._wxPyphantApp.pathToRecipe[-3:] == '.h5':
            if os.path.exists(self._wxPyphantApp.pathToRecipe):
                try:
                    recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(
                        self._wxPyphantApp.pathToRecipe)
                    self._remainingSpace = PyphantCanvas.PyphantCanvas(self, recipe)
                except:
                    self._wxPyphantApp._logger.debug(u"An exception occured while "\
                                       "loading a recipe.",
                                       exc_info=sys.exc_info())
                    wx.MessageBox("An error has occurred while opening "\
                                  "the recipe.\nRecipe has been set to an "\
                                  "empty file in order to prevent data loss.\n"\
                                  "Please investigate the logfile "\
                                  "for further details.\nThe logfile is located at %s"\
                                  % os.path.join(LOGDIR, 'pyphant.log'),
                                  "Recipe broken, unknown format or outdated!")
                    self._wxPyphantApp.pathToRecipe += ".error.h5"
                    self._remainingSpace = PyphantCanvas.PyphantCanvas(self)
            else:
                self._remainingSpace = PyphantCanvas.PyphantCanvas(self)
            from pyphant.core.WebInterface import shorten
            self.SetTitle(self.titleStr \
                          % shorten(self._wxPyphantApp.pathToRecipe, 30, 30))
        else:
            raise IOError('Unknown file format in file "%s"'\
                              % self._wxPyphantApp.pathToRecipe)
        self.recipeState = 'clean'
        self._remainingSpace.diagram.recipe.registerListener(self.recipeChanged)

    def recipeChanged(self, event):
        self.recipeState = 'dirty'

    def onSaveCompositeWorker(self, event=None):
        pyphant.core.PyTablesPersister.saveRecipeToHDF5File(
            self._remainingSpace.diagram.recipe,
            self._wxPyphantApp.pathToRecipe,
            self._fileMenu.IsChecked(wx.ID_FILE4))
        self.recipeState = 'clean'

    def onSaveAsCompositeWorker(self, event=None):
        msg = "Select file to save recipe."
        wc = "Pyphant recipe (*.h5)|*.h5"
        dlg = wx.FileDialog(self, message=msg, defaultDir=os.getcwd(),
                            defaultFile="", wildcard=wc, style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not filename.endswith(".h5"):
                filename += ".h5"
            pyphant.core.PyTablesPersister.saveRecipeToHDF5File(
                self._remainingSpace.diagram.recipe,
                filename,
                self._fileMenu.IsChecked(wx.ID_FILE4))
            self._wxPyphantApp.pathToRecipe = filename
            self.recipeState = 'clean'
            from pyphant.core.WebInterface import shorten
            self.SetTitle(self.titleStr % shorten(filename, 30, 30))
        else:
            dlg.Destroy()

    def _initMenuBar(self):
        self._menuBar = wx.MenuBar()
        self._fileMenu = wx.Menu()
        #self._fileMenu.Append(wx.ID_NEW, "&New\tCTRL+n")
        #self._fileMenu.Append(wx.ID_OPEN, "&Open\tCTRL+o")
        self._fileMenu.AppendCheckItem(wx.ID_FILE4, "Save &results\tCTRL+r")
        self._fileMenu.Check(wx.ID_FILE4, True)
        self._fileMenu.Append(wx.ID_SAVE, "&Save\tCTRL+s")
        self._fileMenu.Append(wx.ID_SAVEAS, "Save &as\tCTRL+a")
        self._fileMenu.Append(wx.ID_EXIT, "E&xit")
        self._menuBar.Append(self._fileMenu, "&File")
        self._closeCompositeWorker = wx.Menu()
        self._closeCompositeWorker.Append(self.ID_CLOSE_COMPOSITE_WORKER,
                                          "&Close Composite Worker")
        self._menuBar.Append(self._closeCompositeWorker,
                              "&Close Composite Worker")
        self._updateMenu = self.createUpdateMenu()
        self._menuBar.Append(self._updateMenu, "&Update")
        self._viewMenu = self.createViewMenu()
        self._menuBar.Append(self._viewMenu, "&View")
        self._kmanagerMenu = self.createKmanagerMenu()
        self._menuBar.Append(self._kmanagerMenu, "&Knowledge Manager")
        self.SetMenuBar(self._menuBar)
        self._menuBar.EnableTop(1, False)
        #self.Bind(wx.EVT_MENU, self.onCreateNew, id=wx.ID_NEW)
        #self.Bind(wx.EVT_MENU, self.onOpenCompositeWorker, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onSaveCompositeWorker, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onSaveAsCompositeWorker, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onCloseCompositeWorker,
                  id=self.ID_CLOSE_COMPOSITE_WORKER)

    def createUpdateMenu(self):
        updateMenu = wx.Menu()
        updateMenu.Append(self.ID_UPDATE_PYPHANT, "Update &Pyphant")
        self.Bind(wx.EVT_MENU, self.onUpdatePyphant, id=self.ID_UPDATE_PYPHANT)
        self.updateIds = { self.ID_UPDATE_PYPHANT : 'pyphant' }
        for toolbox in pkg_resources.iter_entry_points("pyphant.workers"):
            dist = toolbox.dist
            nId = wx.NewId()
            self.updateIds[nId] = dist.key
            updateMenu.Append(nId, "Update %s (%s)"\
                              % (dist.project_name, dist.version))
            self.Bind(wx.EVT_MENU, self.onUpdatePyphant, id=nId)
        return updateMenu

    def createViewMenu(self):
        viewMenu = wx.Menu()
        viewMenu.Append(self.ID_VIEW_WORKERREP, "&Worker Repository")
        viewMenu.Append(self.ID_VIEW_LOGFILE, "&Logfile")
        self.Bind(wx.EVT_MENU, self.onWorkerRep, id=self.ID_VIEW_WORKERREP)
        self.Bind(wx.EVT_MENU, self.onLogfile, id=self.ID_VIEW_LOGFILE)
        return viewMenu

    def createKmanagerMenu(self):
        kmanagerMenu = wx.Menu()
        kmanagerMenu.Append(self.ID_KM_URL, "Import HDF5 or FMF from &URL")
        kmanagerMenu.Append(self.ID_KM_LOCAL, "Import &local HDF5 or FMF file")
        kmanagerMenu.Append(self.ID_KM_ZSTACK_XML, "Import ZStack from &XML")
        kmanagerMenu.Append(self.ID_KM_SHARE, "Start/pause sharing &knowledge")
        self.Bind(wx.EVT_MENU, self.onImportURL, id=self.ID_KM_URL)
        self.Bind(wx.EVT_MENU, self.onImportLocal, id=self.ID_KM_LOCAL)
        self.Bind(wx.EVT_MENU, self.onImportZStackXML, id=self.ID_KM_ZSTACK_XML)
        self.Bind(wx.EVT_MENU, self.onShare, id=self.ID_KM_SHARE)
        return kmanagerMenu

    def onUpdatePyphant(self, event):
        packageName = self._updateMenu.FindItemById(event.Id)\
                      .GetItemLabelText()[7:]
        cpt = u"Update Manager"
        msg = u"Trying to update package '%s'.\nYou will be notified "\
              "when the process has finished.\n"\
              "Please press 'OK' now to begin." % packageName
        dlg = wx.MessageDialog(self, msg, cpt, style=wx.OK|wx.CANCEL)
        dlgid = dlg.ShowModal()
        dlg.Destroy()
        if dlgid != wx.ID_OK:
            return
        try:
            import pyphant.core.UpdateManager
            error = pyphant.core.UpdateManager.updatePackage(
                self.updateIds[event.Id])
        except Exception, exc:
            error = "%s:\n%s" % (exc.__class__.__name__, exc.message)
        if error is not None and len(error) > 0:
            msg = u"An error occured during the update of '%s':\n%s"\
                  % (packageName, error)
        else:
            msg = u"Finished updating '%s'." % packageName
        dlg = wx.MessageDialog(self, msg, cpt, style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onWorkerRep(self, event):
        wrpane = self._auiManager.GetPane(self._workerRepository)
        wrpane.Show(True)
        self._auiManager.Update()

    def onLogfile(self, event):
        logpane = self._auiManager.GetPane(self._logpane)
        logpane.Show(True)
        self._auiManager.Update()

    def onQuit(self,event):
        self.Close()

    def onClose(self, event):
        dlgid = None
        if self.recipeState != 'clean':
            cpt = "Save changed recipe?"
            msg = "The recipe has changed since the last saving.\n"\
                  "Do you want to save before terminating?"
            dlg = wx.MessageDialog(
                self, msg, cpt, style=wx.YES|wx.NO|wx.CANCEL|wx.ICON_QUESTION)
            dlgid = dlg.ShowModal()
            if dlgid == wx.ID_YES:
                self.onSaveCompositeWorker()
            dlg.Destroy()
        if dlgid != wx.ID_CANCEL:
            try:
                self._wxPyphantApp._knowledgeNode.stop()
            except AttributeError:
                pass
            self._auiManager.UnInit()
            self.Destroy()

    def editCompositeWorker(self, worker):
        import PyphantCanvas
        self.compositeWorkerStack.append(self._remainingSpace)
        self._remainingSpace = PyphantCanvas.PyphantCanvas(self, worker)
        self._remainingSpace.diagram.recipe.registerListener(self.recipeChanged)
        self._menuBar.EnableTop(1, True)

    def onCloseCompositeWorker(self, event):
        self._remainingSpace.Destroy()
        self._remainingSpace = self.compositeWorkerStack.pop()
        if len(self.compositeWorkerStack) == 0:
            self._menuBar.EnableTop(1, False)

    def onImportURL(self, event):
        cpt = "Import HDF5 or FMF from URL"
        msg = "Enter a URL to a valid HDF5 or FMF file "\
              "(e.g. http://www.example.org/data.h5).\n"\
              "The file is stored permanently in your home directory in the "\
              ".pyphant directory\nand all DataContainers contained in that "\
              "file are available by using the\nSCSource or DCSource "\
              "Worker even after "\
              "restarting wxPyphant.\nHTTP redirects are resolved "\
              "automatically, i.e. DOIs are supported as well."
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
                dlg2.Destroy()
        dlg.Destroy()

    def onImportLocal(self, event):
        msg = "Select HDF5 or FMF file to import DataContainer(s) from."
        wc = "*.h5, *.hdf, *.hdf5, *.fmf|*.h5;*.hdf;*.hdf5;*.fmf"
        dlg = wx.FileDialog(self, message=msg, defaultDir=os.getcwd(),
                            defaultFile="", wildcard=wc, style=wx.OPEN)
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
                msg2 = "'%s' is not a valid HDF5 or FMF file.\n"\
                       "(Tried to import from '%s')" % (filename, url)
            finally:
                dlg2 = wx.MessageDialog(self, msg2, cpt2, wx.OK)
                dlgid2 = dlg2.ShowModal()
                dlg2.Destroy()
        else:
            dlg.Destroy()

    def onImportZStackXML(self, event):
        msg = "Select XML file to import ZStack from."
        wc = "*.xml|*.xml"
        dlg = wx.FileDialog(self, message=msg, defaultDir=os.getcwd(),
                            defaultFile="", wildcard=wc, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = os.path.realpath(dlg.GetPath())
            from pyphant.core.ZStackManager import (ZStack, ZStackManager)
            tedlg = wx.TextEntryDialog(self, "Enter name for ZStack:",
                                       "", "ZStack")
            if tedlg.ShowModal() == wx.ID_OK:
                name = tedlg.GetValue()
                zsm = ZStackManager()
                try:
                    dummy = zsm.getZStackByName(name)
                    cpt2 = "Error"
                    msg2 = "ZStack %s already exists!" % name
                except ValueError:
                    zstack = ZStack(name=name, xml_file=filename)
                    zsm.addZStack(zstack)
                    cpt2 = "Info"
                    msg2 = "Successfully imported ZStack."
                dlg2 = wx.MessageDialog(self, msg2, cpt2, wx.OK)
                dlg2.ShowModal()
                dlg2.Destroy()
            tedlg.Destroy()
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
        dlg.Destroy()


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
