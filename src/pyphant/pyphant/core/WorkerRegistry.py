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

__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import logging
import singletonmixin
import pkg_resources


class ToolBoxInfo(object):
    def __init__(self, name):
        self.name = name
        self.workerInfos = []
        self._logger = logging.getLogger("pyphant")

    def sortWorkerInfos(self):
        self.workerInfos.sort(key=lambda x:x.name.lower())

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def addWorkerInfo(self, workerInfo):
        if not workerInfo in self.workerInfos:
            self.workerInfos.append(workerInfo)
            self._logger.info("Added worker %s from toolbox %s." \
                              % (workerInfo.name, self.name))


class WorkerRegistry(singletonmixin.Singleton):
    def __init__(self):
        self._toolBoxInfoList = []
        self._toolBoxInfoDict = {}
        self._logger = logging.getLogger("pyphant")
        self._dirty = True

    def registerWorker(self, workerInfo):
        tBI = ToolBoxInfo(workerInfo.toolBoxName)
        if not tBI in self._toolBoxInfoList:
            self._toolBoxInfoList.append(tBI)
            self._toolBoxInfoDict[tBI.name] = tBI
        self._toolBoxInfoDict[tBI.name].addWorkerInfo(workerInfo)

    def sortToolBoxInfos(self):
        for tBI in self._toolBoxInfoList:
            tBI.sortWorkerInfos()
        self._toolBoxInfoList.sort(key=lambda x: x.name.lower())

    def getToolBoxInfoList(self):
        if self._dirty:
            for worker in pkg_resources.iter_entry_points("pyphant.workers"):
                wm = worker.load()
                for module in wm.workers:
                    try:
                        moduleName = worker.module_name + "." + module
                        self._logger.info("Trying to import " + moduleName)
                        exec 'import ' + moduleName
                        try:
                            version = eval(moduleName + ".__version__")
                        except:
                            version = "unknown"
                        self._logger.info("Import module %s in version %s" \
                                          %(moduleName, version))
                    except ImportError, e:
                        self._logger.warning(
                            "worker archive " + worker.module_name \
                            + " contains invalid worker " + module \
                            + ": " + str(e))
            self.sortToolBoxInfos()
            self._dirty = False
        return self._toolBoxInfoList
