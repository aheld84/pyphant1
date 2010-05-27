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
from pyphant.core.PyTablesPersister import loadRecipeFromHDF5File
from tools import Emd5Src
import os
kmanager = KnowledgeManager.getInstance()


class RecipeAlg(object):
    def __init__(self, recipe_fname, result_worker,
                 result_plug, params={}):
        self.recipe_fname = recipe_fname
        self.recipe = loadRecipeFromHDF5File(recipe_fname)
        self.params = params
        self.rwn = result_worker
        self.rpn = result_plug
        self.result_plug = self.recipe.getWorker(
            result_worker).getPlug(result_plug)

    def get_result(self, input_ids, id_only=False, temporary=False):
        from pyphant.core.Helpers import utf82uc
        search_dict = {'attributes':{
            'recipe':utf82uc(self.recipe_fname),
            'result_worker':utf82uc(self.rwn),
            'result_plug':utf82uc(self.rpn),
            'applied_to':utf82uc(input_ids.__repr__()),
            'params':utf82uc(self.params.__repr__())}}
        result_ids = kmanager.search(['id'], search_dict)
        if len(result_ids) > 0 and not temporary:
            if id_only:
                return result_ids[0][0]
            else:
                return kmanager.getDataContainer(result_ids[0][0])
        else:
            # Fill open sockets:
            for wname, sockets in input_ids.iteritems():
                worker = self.recipe.getWorker(wname)
                for sname, emd5 in sockets.iteritems():
                    socket = worker.getSocket(sname)
                    dummy = Emd5Src.Emd5Src()
                    dummy.paramSelectby.value = u"enter emd5"
                    dummy.paramEnteremd5.value = emd5
                    socket.insert(dummy.getPlugs()[0])
            # Set parameters:
            for wname, wparams in self.params.iteritems():
                for pname, pvalue in wparams.iteritems():
                    self.recipe.getWorker(wname).getParam(pname).value = pvalue
            # Get Result
            result_dc = self.result_plug.getResult()
            # Pull plugs
            for wname, sockets in input_ids.iteritems():
                worker = self.recipe.getWorker(wname)
                for sname, emd5 in sockets.iteritems():
                    worker.getSocket(sname).pullPlug()
            result_dc.attributes['recipe'] = utf82uc(self.recipe_fname)
            result_dc.attributes['applied_to'] = utf82uc(input_ids.__repr__())
            result_dc.attributes['params'] = utf82uc(self.params.__repr__())
            result_dc.attributes['result_plug'] = utf82uc(self.rpn)
            result_dc.attributes['result_worker'] = utf82uc(self.rwn)
            kmanager.registerDataContainer(result_dc, temporary=temporary)
            if id_only:
                return result_dc.id
            else:
                return result_dc

    def get_batch_result_id(self, input_ids, column='emd5', update_attrs={},
                            subscriber=0, start=1, end=100, temporary=False):
        subscriber %= start
        from pyphant.core.Helpers import utf82uc
        search_dict = {'attributes':{
            'batch_recipe':utf82uc(self.recipe_fname),
            'result_worker':utf82uc(self.rwn),
            'result_plug':utf82uc(self.rpn),
            'applied_to':utf82uc(input_ids.__repr__()),
            'params':utf82uc(self.params.__repr__())}}
        result_ids = kmanager.search(['id'], search_dict)
        if len(result_ids) > 0:
            subscriber %= end
            return result_ids[0][0]
        import copy
        input_scs = dict([(wname, dict([(sname, kmanager.getDataContainer(emd5)) \
                                        for sname, emd5 in sockets.iteritems()])) \
                          for wname, sockets in input_ids.iteritems()])
        out_column = []
        ref_sc = input_scs.values()[0].values()[0]
        output_sc = copy.deepcopy(ref_sc)
        import numpy
        sharpruns = len(ref_sc[column].data)
        import math
        for index in xrange(sharpruns):
            subscriber %= 1 + math.floor(start + float((end - start) * index) \
                                         / sharpruns)
            ids = dict([(wname, dict([(sname, unicode(isc[column].data[index])) \
                                      for sname, isc in sockets.iteritems()])) \
                        for wname, sockets in input_scs.iteritems()])
            out_column.append(self.get_result(ids, id_only=True,
                                              temporary=temporary))
        output_sc[column].data = numpy.array(out_column)
        output_sc.longname = "%s_%s" % (os.path.basename(self.recipe_fname),
                                        ref_sc.longname)
        output_sc.attributes['batch_recipe'] = utf82uc(self.recipe_fname)
        output_sc.attributes['applied_to'] = utf82uc(input_ids.__repr__())
        output_sc.attributes['result_plug'] = utf82uc(self.rpn)
        output_sc.attributes['result_worker'] = utf82uc(self.rwn)
        output_sc.attributes['params'] = utf82uc(self.params.__repr__())
        output_sc.attributes.update(update_attrs)
        output_sc.seal()
        kmanager.registerDataContainer(output_sc, temporary=temporary)
        subscriber %= end
        return output_sc.id
