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
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param
from pyphant.core.ZStackManager import ZStackManager
from pyphant.core.RecipeAlg import RecipeAlg
from tools.Emd5Src import HiddenValue
import ImageProcessing
import os


class ZStacks(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "ZStacks"
    _params = [("zstack", u"ZStack", [u'None'], None),
               ("rpath", u"Path to recipes (select any file)", "",
                Connectors.SUBTYPE_FILE),
               ("gradient_recipe", u"Gradient recipe", [u'None'], None),
               ("label_recipe", u"Label recipe", [u'None'], None),
               #("cutoff", u"Cutoff", "100 mum", None),
               ("median_size", u"Median size", 5, None)]

    def refreshParams(self, subscriber=None):
        zstacks = ZStackManager().getZStacks()
        pvalues = []
        for zstack in zstacks:
            hvalue = HiddenValue(zstack.repr_sc.longname)
            hvalue.setHiddenValue(zstack)
            pvalues.append(hvalue)
        pvalues.sort()
        self.paramZstack.possibleValues = pvalues
        directory = os.path.dirname(self.paramRpath.value)
        if os.path.isdir(directory):
            pvalues = filter(
                lambda x: x.endswith('.h5'),
                os.listdir(directory))
            pvalues.sort()
            self.paramGradient_recipe.possibleValues = pvalues
            self.paramLabel_recipe.possibleValues = pvalues

    def get_rp_ga_la(self):
        gradient_recipe = self.paramGradient_recipe.value
        label_recipe = self.paramLabel_recipe.value
        rpath = os.path.dirname(os.path.realpath(self.paramRpath.value))
        gradient_alg = RecipeAlg(os.path.join(rpath, gradient_recipe),
                                 'gradient', 'gradientWorker',
                                 {'median':{'size':self.paramMedian_size.value}})
        label_alg = RecipeAlg(os.path.join(rpath, label_recipe),
                              'label', 'ndimage')
        return (rpath, gradient_alg, label_alg)

    @Worker.plug(Connectors.TYPE_ARRAY)
    def statistics(self, subscriber=0):
        #cutoff = self.paramCutoff.value
        try:
            rpath, gradient_alg, label_alg = self.get_rp_ga_la()
        except IOError:
            return None
        self.paramZstack.value.hiddenvalue.recipe_path = rpath
        return self.paramZstack.value.hiddenvalue.get_statistics(
            gradient_alg, label_alg, subscriber=subscriber)

    @Worker.plug(Connectors.TYPE_ARRAY)
    def raw_image(self, subscriber=0):
        return self.paramZstack.value.hiddenvalue.repr_sc

    @Worker.plug(Connectors.TYPE_ARRAY)
    def mf_human(self, subscriber=0):
        try:
            rpath, gradient_alg, label_alg = self.get_rp_ga_la()
        except IOError:
            return None
        self.paramZstack.value.hiddenvalue.recipe_path = rpath
        return self.paramZstack.value.hiddenvalue.get_human_imgs(
            gradient_alg, label_alg, subscriber=subscriber)
