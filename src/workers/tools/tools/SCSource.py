# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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

"""
This module provides a worker for importing SampleConainers from the
KnowledgeManager into wxPyphant.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, Param)
from DCSource import (ANYSTR, DCSource)
from pyphant.core.KnowledgeManager import KnowledgeManager
from pyphant.core.Connectors import SUBTYPE_INSTANT

class SCSource(DCSource, Worker.Worker):
    """
    This worker provides instantly updated dropdown lists for selecting
    a SampleContainer from the KnowledgeManager.
    """
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "SampleContainer"
    _params = [("longname", u"and longname ==", [ANYSTR], SUBTYPE_INSTANT),
               ("shortname", u"and shortname ==", [ANYSTR], SUBTYPE_INSTANT),
               ("has_col", u"and has column", [ANYSTR], SUBTYPE_INSTANT),
               ("col_of", u"and is column of", [ANYSTR], SUBTYPE_INSTANT),
               ("machine", u"machine ==", [ANYSTR], SUBTYPE_INSTANT),
               ("creator", u"and creator ==", [ANYSTR], SUBTYPE_INSTANT),
               ("id", u"and emd5 ==", [ANYSTR], SUBTYPE_INSTANT),
               ('reset', u'clear all parameters', False, SUBTYPE_INSTANT)]

    def __init__(self, *args, **kargs):
        Worker.Worker.__init__(self, *args, **kargs)
        DCSource.__init__(self, 'sample')

    @Worker.plug(Connectors.TYPE_ARRAY)
    def getSampleContainer(self, subscriber = 0):
        emd5 = self.paramId.value
        kmanager = KnowledgeManager.getInstance()
        return kmanager.getDataContainer(emd5)
