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
kmanager = KnowledgeManager.getInstance()

def load_recipe(filename):
    recipe_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'recipes')
    path = os.path.join(recipe_path, filename)
    return loadRecipeFromHDF5File(path)


class RecipeAlg(object):
    def __init__(self, recipe_name, result_worker, params={}):
        self.recipe_name = recipe_name
        self.recipe = load_recipe(recipe_name)
        self.params = params
        for worker, wparams in params.iteritems():
            for pname, pvalue in wparams.iteritems():
                recipe.getWorker(worker).getParam(pname) = pvalue
        self.result_plug = recipe.getWorker(result_worker).getPlugs()[0]
        self.input_socket = recipe.getOpenSocketsForPlug(result_plug)[0]
        from tools import Emd5Src
        self.dummy = Emd5Src.Emd5Src()
        self.dummy.paramSelectby.value = u"enter emd5"

    def get_result(input_id, id_only=False, temporary=False):
        result_ids = kmanager.search(['id'], {'attributes':{
            'recipe':self.recipe_name,
            'applied_to':input_id,
            'params':self.params.__repr__()}})
        if len(result_ids) > 0 and not temporary:
            if id_only:
                return result[0][0]
            else:
                return kmanager.getDataContainer(result[0][0])
        else:
            self.input_socket.insert(self.dummy.getPlugs()[0])
            self.dummy.paramEnteremd5.value = input_id
            result_dc = self.result_plug.getResult()
            self.input_socket.pullPlug()
            result_dc.attributes['recipe'] = self.recipe_name
            result_dc.attributes['applied_to'] = input_id
            resutl_dc.attributes['params'] = self.params.__repr__()
            if not temporary:
                kmanager.registerDataContainer(result_dc)
            if id_only:
                return result_dc.id
            else:
                return result_dc

    def get_batch_result_id(self, input_id, column='emd5'):
        input_sc = kmanager.getDataContainer(input_id)
        import copy
        output_sc = copy.deepcopy(input_sc)
        input_emd5s = input_sc[column].data
        import numpy
        output_sc[column].data = numpy.array(
            [self.get_result(emd5, id_only=True) for emd5 in input_emd5s])
        output_sc.longname = "%s_%s" % (self.recipe_name, input_sc.longname)
        output_sc.seal()
        kmanager.registerDataContainer(output_sc, temporary=True)
        return output_sc.id
