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


from pyphant.core.XMLHandler import getXMLRoot
from pyphant.quantities import Quantity
from pyphant.core.DataContainer import (FieldContainer, SampleContainer)
import scipy
import Image
from pyphant.core.KnowledgeManager import KnowledgeManager
from pyphant.core.RecipeAlg import RecipeAlg
import os
kmanager = KnowledgeManager.getInstance()

def getImageFCs(images_meta):
    zvalues = []
    emd5s = []
    files = []
    for img_meta in images_meta:
        files.append(img_meta['filename'])
        img = Image.open(img_meta['filename'])
        data = scipy.misc.fromimage(img, flatten=True)
        zvalue = img_meta['z-pos']
        ydata = scipy.arange(img_meta['height']) \
                * img_meta['pixel_height'].value \
                + img_meta['y-pos'].value
        xdata = scipy.arange(img_meta['width']) \
                * img_meta['pixel_width'].value \
                + img_meta['x-pos'].value
        dimensions = [FieldContainer(ydata,
                                     unit=Quantity(1.0, 'mum'),
                                     longname=u'y-axis',
                                     shortname=u'y'),
                      FieldContainer(xdata,
                                     unit=Quantity(1.0, 'mum'),
                                     longname=u'x-axis',
                                     shortname=u'x')]
        fcattr = {u'filename': img_meta['filename'],
                  u'zvalue': zvalue,
                  u'pxx': img_meta['id'],
                  u'timestamp': img_meta['timestamp']}
        img_fc = FieldContainer(data=data,
                                longname=os.path.basename(img_meta['filename']),
                                shortname="image",
                                dimensions=dimensions, attributes=fcattr)
        img_fc.seal()
        kmanager.registerDataContainer(img_fc)
        emd5s.append(img_fc.id)
        zvalues.append(zvalue.value)
    if len(zvalues) == 0:
        return None, None, None
    zfc = FieldContainer(scipy.array(zvalues), longname='z-value',
                         shortname='z', unit=Quantity(1.0, 'mum'))
    filefc = FieldContainer(scipy.array(files), longname='filename',
                            shortname='f')
    emd5fc = FieldContainer(scipy.array(emd5s), longname='emd5', shortname='i')
    return zfc, filefc, emd5fc


class ZStack(object):
    def __init__(self, sc_id=None, name=None, image_path=None,
                 extension='.tif', ztol=None):
        """Initializes a ZStack from an existing id or a local source"""
        assert (sc_id is None) is not (image_path is None)
        self._recipe_path = None
        self.ztol = ztol
        if sc_id is not None:
            self.repr_sc = kmanager.getDataContainer(sc_id)
        else:
            assert name is not None and ztol is not None
            self.repr_sc = self._import_zstack(name,
                                               os.path.realpath(image_path),
                                               extension)

    def _import_zstack(self, name, path, extension):
        def file_filter(name):
            return os.path.isfile(name) and name.endswith(extension)
        file_names = filter(file_filter,
                            [os.path.join(path, entry) \
                             for entry in os.listdir(path)])
        file_names.sort()
        # TODO
        #images_meta = ...
        zfc, filefc, emd5fc = getImageFCs(images_meta)
        if zfc == None:
            return None
        attributes = {}
        attributes['ztol'] = ztol.__repr__()
        attributes['isZStack'] = 'yes'
        ssc = SampleContainer([zfc, filefc, emd5fc],
                              name,
                              "z-stack",
                              attributes)
        ssc.seal()
        kmanager.registerDataContainer(ssc)
        return ssc

    def _set_recipe_path(self, rpath):
        self._recipe_path = os.path.realpath(rpath)

    def _get_recipe_path(self):
        return self._recipe_path
    recipe_path = property(_get_recipe_path, _set_recipe_path)

    def _get_mf_id(self, gradient_alg, label_alg, human):
        assert self._recipe_path is not None
        uattr = {'isZStack':'no'}
        in_ids = {'grey_invert':{'image':self.repr_sc.id}}
        gradient_id = gradient_alg.get_batch_result_id(in_ids, update_attrs=uattr)
        in_ids = {'threshold':{'image':gradient_id}}
        label_id = label_alg.get_batch_result_id(in_ids, update_attrs=uattr)
        mf_alg = RecipeAlg(os.path.join(self.recipe_path, 'MeasureFocus.h5'),
                           'MeasureFocus', 'measure_focus',
                           {'MeasureFocus':{'humanOutput':human}})
        in_ids = {'MeasureFocus':{'image':gradient_id,
                                  'labels':label_id}}
        return mf_alg.get_batch_result_id(in_ids, update_attrs=uattr)

    def get_statistics(self, gradient_alg, label_alg, cutoff):
        mf_id = self._get_mf_id(gradient_alg, label_alg, False)
        af_alg = RecipeAlg(os.path.join(self.recipe_path, 'AutoFocus.h5'),
                           'AutoFocus', 'AutoFocusWorker')
        in_ids = {'AutoFocus':{'focusSC':mf_id}}
        af_id = af_alg.get_result(in_ids, id_only=True)
        params = {'Cutoff':{'expression':'"d" <= %s' % cutoff},
                  'ColumnExtractor':{'column':'diameter'}}
        stat_alg = RecipeAlg(os.path.join(self.recipe_path, 'Statistics.h5'),
                             'ColumnExtractor', 'extract', params)
        in_ids = {'Cutoff':{'table':af_id}}
        return stat_alg.get_result(in_ids, temporary=True)

    def get_human_imgs(self, gradient_alg, label_alg):
        mf_id = self._get_mf_id(gradient_alg, label_alg, True)
        return kmanager.getDataContainer(mf_id)


class ZStackManager(object):
    def addZStack(self, zstack):
        """Adds a given zstack to the pool"""
        kmanager.registerDataContainer(zstack.repr_sc)

    def getZStacks(self):
        """Returns a list of all ZStacks in the pool"""
        search_dict = {'type':'sample', 'attributes':{'isZStack':'yes'}}
        search_result = kmanager.search(['id'], search_dict)
        if len(search_result) == 0:
            return []
        return [ZStack(zs_id[0]) for zs_id in search_result]
