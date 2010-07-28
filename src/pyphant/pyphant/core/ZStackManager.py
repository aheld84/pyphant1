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


from pyphant.quantities import Quantity
from pyphant.core.DataContainer import (FieldContainer, SampleContainer)
import scipy
import Image
from pyphant.core.KnowledgeManager import KnowledgeManager
import os
import re
kmanager = KnowledgeManager.getInstance()


class ZStack(object):
    def __init__(self, sc_id=None, meta=None, temporary=False):
        """Initializes a ZStack from an existing id or metadata"""
        assert (sc_id is None) is not (meta is None)
        self.temporary = temporary
        if sc_id is not None:
            self.repr_sc = kmanager.getDataContainer(sc_id)
        else:
            self.repr_sc = self._import_zstack(meta)

    @staticmethod
    def _get_image_fcs(images_meta, temporary=False):
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
                pdial.Update(count, os.path.basename(img_meta['imgFilename']))
                count += 1
            files.append(img_meta['xmlFilename'])
            img = Image.open(img_meta['imgFilename'])
            data = scipy.misc.fromimage(img, flatten=True)
            zvalue = img_meta['z-pos']
            yunit = Quantity(1.0, img_meta['height'].unit)
            xunit = Quantity(1.0, img_meta['width'].unit)
            ydata = scipy.arange(img_meta['height[pixel]']) \
                    * img_meta['y-factor'].inUnitsOf(yunit.unit).value \
                    + img_meta['y-pos'].inUnitsOf(yunit.unit).value
            xdata = scipy.arange(img_meta['width[pixel]']) \
                    * img_meta['x-factor'].inUnitsOf(xunit.unit).value \
                    + img_meta['x-pos'].inUnitsOf(xunit.unit).value
            dimensions = [FieldContainer(ydata,
                                         unit=yunit,
                                         longname=u'y-axis',
                                         shortname=u'y'),
                          FieldContainer(xdata,
                                         unit=xunit,
                                         longname=u'x-axis',
                                         shortname=u'x')]
            fcattr = {'vmin':0, 'vmax':255}
            fcattr.update(img_meta)
            img_fc = FieldContainer(data=data,
                                    longname=os.path.basename(
                                        img_meta['imgFilename']),
                                    shortname="i",
                                    dimensions=dimensions, attributes=fcattr)
            img_fc.seal()
            kmanager.registerDataContainer(img_fc, temporary=temporary)
            emd5s.append(img_fc.id)
            zvalues.append(zvalue.value)
        if len(zvalues) == 0:
            return None, None, None
        zfc = FieldContainer(scipy.array(zvalues), longname='z-value',
                             shortname='z', unit=Quantity(1.0, zvalue.unit))
        filefc = FieldContainer(scipy.array(files), longname='filename',
                                shortname='f')
        emd5fc = FieldContainer(scipy.array(emd5s), longname='emd5',
                                shortname='i')
        if pdial is not None:
            pdial.Destroy()
        return zfc, filefc, emd5fc

    def _import_zstack(self, meta):
        zfc, filefc, emd5fc = ZStack._get_image_fcs(meta, self.temporary)
        if zfc == None:
            return None
        attributes = {}
        attributes['ZStackType'] = 'RawSC'
        attributes['xmlFilename'] = meta[0]['xmlFilename']
        attributes['crystal'] = meta[0]['crystal']
        ssc = SampleContainer([zfc, filefc, emd5fc],
                              meta[0]['ZStackName'],
                              "z",
                              attributes)
        ssc.seal()
        kmanager.registerDataContainer(ssc, temporary=self.temporary)
        return ssc


class ZStackManager(object):
    def importZStack(self, xmlFName, name, crystal, temporary=False):
        metaReader = getMetaReader(xmlFName, name, crystal)
        meta = metaReader.getMeta()
        return ZStack(meta=meta, temporary=temporary)

    def getZStacks(self):
        """Returns a list of all ZStacks in the pool"""
        search_dict = {'type':'sample', 'attributes':{'ZStackType':'RawSC'}}
        search_result = kmanager.search(['id'], search_dict)
        if len(search_result) == 0:
            return []
        return [ZStack(zs_id[0]) for zs_id in search_result]

    def getZStackByName(self, name):
        search_dict = {'type':'sample', 'attributes':{'ZStackType':'RawSC'},
                       'longname':name}
        sresult = kmanager.search(['id'], search_dict)
        if sresult == []:
            raise ValueError("There is no ZStack called %s!" \
                                 % name)
        return ZStack(sc_id=sresult[0][0])


class MetaReader(object):
    def __init__(self, xmlFName, name, crystal):
        self.xmlFName = xmlFName
        from pyphant.core.XMLHandler import getXMLRoot
        self.xmlRoot = getXMLRoot(xmlFName)
        self.zStackName = name
        self.crystal = crystal

    def getMeta(self):
        getStr = lambda x: x.content.strip()
        def getTag(tag, tagstr):
            for subtag in tagstr.split(':'):
                tag = tag[subtag]
            return tag
        common_meta = {}
        for key, tagstr in self.commonTagDict.iteritems():
            common_meta[key] = getStr(getTag(self.xmlRoot, tagstr))
        common_meta['xmlFilename'] = self.xmlFName
        images_meta = []
        for ztag in [value for key, value in self.xmlRoot.children.iteritems()\
                     if self.tagRe.match(key) is not None]:
            meta = common_meta.copy()
            for key, tagstr in self.imageTagDict.iteritems():
                meta[key] = getStr(getTag(ztag, tagstr))
            meta['zid'] = self.getZId(ztag.name)
            meta['pid'] = self.getPId(ztag.name)
            meta['imgFilename'] = self.getImgFName(ztag.name)
            meta['ZStackName'] = self.zStackName
            meta['crystal'] = self.crystal
            images_meta.append(meta)
        self.validateMeta(images_meta)
        images_meta.sort(key = lambda x: x['z-pos'].value)
        return images_meta


class ZStackMetaReader(MetaReader):
    commonTagDict = {'scalingfactor 0':'Scaling:Factor_0',
                     'scalingfactor 1':'Scaling:Factor_1',
                     'SF type 0':'Scaling:Type_0',
                     'SF type 1':'Scaling:Type_1',
                     'width[pixel]':'Tags:V25',
                     'height[pixel]':'Tags:V26',
                     'width':'Tags:V30',
                     'height':'Tags:V33',
                     'width type':'Tags:V28',
                     'height type':'Tags:V31',
                     'x-factor':'Tags:V29',
                     'y-factor':'Tags:V32',
                     'x-pos':'Tags:V48',
                     'y-pos':'Tags:V49',
                     'objective':'Tags:V101'}
    imageTagDict = {'timestamp':'Tags:V44',
                    'z-pos':'Tags:V93'}
    tagRe = re.compile(r'^z[0-9]+$')

    def getImgFName(self, ztagname):
        fname = self.xmlRoot['Tags']['V5'].content.strip()
        root, ext = os.path.splitext(fname)
        fname = "%s_%s%s" % (root, ztagname, ext)
        return os.path.join(os.path.dirname(self.xmlFName), fname)

    def getZId(self, ztagname):
        return int(ztagname[1:])

    def getPId(self, ztagname):
        return 0

    def validateMeta(self, meta):
        getFloat = lambda x: float(x.replace(',', '.'))
        getMum = lambda x: Quantity(getFloat(x), 'mum')
        mumErr = 'Expected micrometre but got different unit!'
        for img_meta in meta:
            assert img_meta.pop('SF type 0') == '76', mumErr
            assert img_meta.pop('SF type 1') == '76', mumErr
            assert img_meta.pop('width type') == '76', mumErr
            assert img_meta.pop('height type') == '76', mumErr
            assert getFloat(img_meta.pop('scalingfactor 0')) \
                   == getFloat(img_meta['x-factor'])
            assert getFloat(img_meta.pop('scalingfactor 1')) \
                   == getFloat(img_meta['y-factor'])
            for key in ['width', 'height', 'x-factor', 'y-factor', 'x-pos',
                        'y-pos', 'z-pos']:
                img_meta[key] = getMum(img_meta[key])
            for key in ['width[pixel]', 'height[pixel]']:
                img_meta[key] = int(img_meta[key])
            assert img_meta['width[pixel]'] == int(round(img_meta['width'] /\
                   img_meta['x-factor'])), "x scaling is void"
            assert img_meta['height[pixel]'] == int(round(img_meta['height'] /\
                   img_meta['y-factor'])), "y scaling is void"


class SingleMetaReader(ZStackMetaReader):
    commonTagDict = {'scalingfactor 0':'Scaling:Factor_0',
                     'scalingfactor 1':'Scaling:Factor_1',
                     'SF type 0':'Scaling:Type_0',
                     'SF type 1':'Scaling:Type_1',
                     'width[pixel]':'Tags:V11',
                     'height[pixel]':'Tags:V12',
                     'width':'Tags:V16',
                     'height':'Tags:V19',
                     'width type':'Tags:V14',
                     'height type':'Tags:V17',
                     'x-factor':'Tags:V15',
                     'y-factor':'Tags:V18',
                     'x-pos':'Tags:V41',
                     'y-pos':'Tags:V42',
                     'objective':'Tags:V93',
                     'timestamp':'Tags:V50',
                     'z-pos':'Tags:V99'}
    imageTagDict = {}
    tagRe = re.compile(r'^_single$')

    def getZId(self, ztagname):
        return 0

    def getImgFName(self, ztagname):
        fname = self.xmlRoot['Tags']['V5'].content.strip()
        return os.path.join(os.path.dirname(self.xmlFName), fname)

META_READERS = [ZStackMetaReader, SingleMetaReader]

def getMetaReader(xml, name, crystal):
    from pyphant.core.XMLHandler import getXMLRoot
    root = getXMLRoot(xml)
    matched = False
    for key in root.children.iterkeys():
        for mreader in META_READERS:
            if mreader.tagRe.match(key) is not None:
                matched = True
                break
        if matched:
            break
    if matched:
        return mreader(xml, name, crystal)
    else:
        raise ValueError("Unknown file format in file: %s" % xml)
