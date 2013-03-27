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

__version__ = "$Revision$"
# $Source$

from pyphant.core import Connectors, singletonmixin
import logging, pkg_resources

class DataVisReg(singletonmixin.Singleton):

    def __init__(self):
        self._registry={}
        self._logger = logging.getLogger("pyphant")
        self._logger.info("Initialized DataVisReg")
        self._dirty = True

    def registerVisualizer(self, dataType, visualizer):
        if not dataType in self._registry:
            self._logger.info('Added new dataType "%s"'%dataType)
            self._registry[dataType]=[]
        if not visualizer in self._registry[dataType]:
            self._logger.info('Added visualizer "%s" to dataType "%s"'%(visualizer,dataType))
            self._registry[dataType].append(visualizer)

    def getVisualizers(self, dataType):
        if self._dirty:
            for vis in pkg_resources.iter_entry_points("pyphant.visualizers"):
                vm = vis.load()
                self.registerVisualizer(vis.name, vm)
            self._dirty = False
        try:
            return self._registry[dataType]
        except KeyError:
            return []

import pyphant.visualizers
