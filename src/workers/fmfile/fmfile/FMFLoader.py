# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009-2010, Andreas W. Liehr (liehr@users.sourceforge.net)
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
The FMF Loader is a class of Pyphant's FMF Toolbox. It loads an FMF
file from the location given in the worker's configuration.
"""


import os.path
from pyphant.core import (Worker, Connectors)
from pyphant.core.LoadFMF import loadFMFFromFile


class FMFLoader(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Load FMF files"

    _params = [("filename", u"Filename", "", Connectors.SUBTYPE_FILE)]

    def inithook(self):
        fileMask = "FMF and FMF-ZIP (*.fmf, *.zip)|*.fmf;*.zip|FMF (*.fmf)|" \
                   "*.fmf|FMF-ZIP (*.zip)|*.zip|All files (*)|*"
        self.paramFilename.fileMask = fileMask

    @Worker.plug(Connectors.TYPE_ARRAY)
    def loadFMF(self, subscriber=0):
        filename = self.paramFilename.value
        if not os.path.exists(filename):
            raise RuntimeError("Opening non existent file: "+filename)
        result = loadFMFFromFile(filename, subscriber)
        result.seal()
        return result
