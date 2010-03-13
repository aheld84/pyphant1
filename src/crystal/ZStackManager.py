#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
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

u"""Provides ZStackManager
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

from pyphant.core.KnowledgeManager import KnowledgeManager
import os
kmanager = KnowledgeManager.getInstance()


class ZStack(object):
    def __init__(self, sc_id=None, path=None, extension='.tif'):
        """Initializes a ZStack from an existing id or a local source"""
        assert (sc_id is None) is not (path is None)
        if sc_id is not None:
            self.repr_sc = kmanager.getDataContainer(sc_id)
        else:
            self.repr_sc = self._import_zstack(os.path.realpath(path))

    def _import_zstack(self, path):
        def file_filter(name):
            return os.path.isfile(name) and name.endswith(extension)
        file_names = filter(file_filter,
                            [os.path.join(path, entry) \
                             for entry in os.listdir(path)])
        # TODO

    def get_histogram(self, mf_alg, bins=100, cutoff=u'100 mum'):
        params = {'Histogram':{'bins':bins},
                  'Cutoff':{'expression':'"d" <= %s' % cutoff}}
        af_alg = RecipeAlg('AutoFocus.h5', 'AutoFocus')
        histo_alg = RecipeAlg('Statistics.h5', 'Histogram', params)
        return histo_alg.get_result(
            af_alg.get_result(
                mf_alg.get_batch_result_id(self.repr_sc.id),
                id_only=True),
            temporary=True)


class ZStackManager(object):
    def addZStack(self, zstack):
        """Adds a given zstack to the pool"""
        kmanager.registerDataContainer(zstack.repr_sc)

    def getZStacks(self):
        """Returns a list of all ZStacks in the pool"""
        serch_dict = {'type':'sample', 'attributes':{'isZStack':'yes'}}
        return [ZStack(zs_id[0]) for zs_id in km.search(['id'], search_dict)[0]]
