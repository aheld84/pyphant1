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


class ZStack(object):
    def __init__(self, sc_id=None, name=None, xml_file=None):
        """Initializes a ZStack from an existing id or a local source"""
        assert (sc_id is None) is not (xml_file is None)
        self._recipe_path = None
        if sc_id is not None:
            self.repr_sc = kmanager.getDataContainer(sc_id)
        else:
            assert name is not None
            self.repr_sc = self._import_zstack(name,
                                               os.path.realpath(xml_file))

    @staticmethod
    def _get_images_meta(xml_file):
        def getFloat(xmlelement):
            return float(xmlelement.content.strip().replace(',', '.'))

        def getMum(xmlelement):
            return Quantity(getFloat(xmlelement), 'mum')

        base_path = os.path.dirname(xml_file)
        xml_root = getXMLRoot(xml_file)
        images_meta = []
        for ztag in [value for key, value in xml_root.children.iteritems()\
                     if key.startswith('z')]:
            meta = {}
            fname = xml_root['Tags']['V5'].content.strip()
            root, ext = os.path.splitext(fname)
            fname = "%s_%s%s" % (root, ztag.name, ext)
            meta['img_filename'] = os.path.join(base_path, fname)
            meta['zvi_filename'] = os.path.join(
                base_path, xml_root['Tags']['V150'].content.strip())
            meta['xml_filename'] = xml_file
            meta['zid'] = ztag.name
            ztag = ztag['Tags']
            meta['timestamp'] = ztag['V44'].content.strip()
            meta['width'] = int(ztag['V3'].content.strip())
            meta['height'] = int(ztag['V4'].content.strip())
            meta['x-pos'] = getMum(ztag['V15'])
            meta['y-pos'] = getMum(ztag['V16'])
            meta['z-pos'] = getMum(ztag['V93'])
            meta['pixel_width'] = getMum(xml_root['Scaling']['Factor_0'])
            meta['pixel_height'] = getMum(xml_root['Scaling']['Factor_1'])
            images_meta.append(meta)
        images_meta.sort(key = lambda x: x['z-pos'].value)
        return images_meta

    @staticmethod
    def _get_image_fcs(images_meta):
        zvalues = []
        emd5s = []
        files = []
        from wx import (ProgressDialog, PyNoAppError)
        try:
            pdial = ProgressDialog('Importing ZStack...', ' ' * 50,
                                   maximum=len(images_meta))
        except PyNoAppError:
            pdial = None
        count = 1
        for img_meta in images_meta:
            if pdial is not None:
                pdial.Update(count, os.path.basename(img_meta['img_filename']))
                count += 1
            files.append(img_meta['xml_filename'])
            img = Image.open(img_meta['img_filename'])
            data = scipy.misc.fromimage(img, flatten=True)
            zvalue = img_meta['z-pos']
            ydata = scipy.arange(img_meta['height']) \
                    * img_meta['pixel_height'].inUnitsOf('mum').value \
                    + img_meta['y-pos'].inUnitsOf('mum').value
            xdata = scipy.arange(img_meta['width']) \
                    * img_meta['pixel_width'].inUnitsOf('mum').value \
                    + img_meta['x-pos'].inUnitsOf('mum').value
            dimensions = [FieldContainer(ydata,
                                         unit=Quantity(1.0, 'mum'),
                                         longname=u'y-axis',
                                         shortname=u'y'),
                          FieldContainer(xdata,
                                         unit=Quantity(1.0, 'mum'),
                                         longname=u'x-axis',
                                         shortname=u'x')]
            fcattr = {'img_filename':img_meta['img_filename'],
                      'xml_filename':img_meta['xml_filename'],
                      'zvi_filename':img_meta['zvi_filename'],
                      'zvalue':zvalue,
                      'timestamp':img_meta['timestamp'],
                      'zid':img_meta['zid']}
            img_fc = FieldContainer(data=data,
                                    longname=os.path.basename(
                                        img_meta['img_filename']),
                                    shortname="img",
                                    dimensions=dimensions, attributes=fcattr)
            img_fc.seal()
            kmanager.registerDataContainer(img_fc)
            emd5s.append(img_fc.id)
            zvalues.append(zvalue.inUnitsOf('mum').value)
        if len(zvalues) == 0:
            return None, None, None
        zfc = FieldContainer(scipy.array(zvalues), longname='z-value',
                             shortname='z', unit=Quantity(1.0, 'mum'))
        filefc = FieldContainer(scipy.array(files), longname='filename',
                                shortname='f')
        emd5fc = FieldContainer(scipy.array(emd5s), longname='emd5', shortname='i')
        if pdial is not None:
            pdial.Destroy()
        return zfc, filefc, emd5fc

    @staticmethod
    def _estimate_ztol(zfc):
        zmums = [(float(zvalue) * zfc.unit).inUnitsOf('mum').value \
                 for zvalue in zfc.data]
        zmums.sort()
        diffs = []
        for index in xrange(len(zmums) - 1):
            diffs.append(zmums[index + 1] - zmums[index])
        return Quantity(2.0 * sum(diffs) / float(len(diffs)), 'mum')

    def _import_zstack(self, name, xml_file):
        images_meta = ZStack._get_images_meta(xml_file)
        zfc, filefc, emd5fc = ZStack._get_image_fcs(images_meta)
        if zfc == None:
            return None
        attributes = {}
        attributes['ztol'] = ZStack._estimate_ztol(zfc)
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

    def get_statistics(self, gradient_alg, label_alg):
        mf_id = self._get_mf_id(gradient_alg, label_alg, False)
        af_alg = RecipeAlg(os.path.join(self.recipe_path, 'AutoFocus.h5'),
                           'AutoFocus', 'AutoFocusWorker')
        in_ids = {'AutoFocus':{'focusSC':mf_id}}
        af_sc = af_alg.get_result(in_ids)
        return af_sc
        #params = {'Cutoff':{'expression':'"d" <= %s' % cutoff},
        #          'ColumnExtractor':{'column':'diameter'}}
        #stat_alg = RecipeAlg(os.path.join(self.recipe_path, 'Statistics.h5'),
        #                     'ColumnExtractor', 'extract', params)
        #in_ids = {'Cutoff':{'table':af_id}}
        #return stat_alg.get_result(in_ids, temporary=True)

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
