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
This module provides the refactored AutoFocus Worker and its little helpers
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer
import ImageProcessing
import numpy, copy
from scipy import ndimage
from pyphant.quantities import Quantity
from pyphant.core.DataContainer import (FieldContainer, SampleContainer)

def almost(val1, val2, error=0.01):
    return abs(val2 - val1) <= error


class ZSUnits(object):
    FQUANT = Quantity('1.0 mum**-3')
    FUNIT = FQUANT.unit
    AQUANT = Quantity('1.0 mum**2')
    AUNIT = AQUANT.unit
    GQUANT = Quantity('1.0 mum**-1')
    GUNIT = GQUANT.unit
    NODNS = "Non-uniform dimensions not supported!"
    DXDY = NODNS + "\ndy = %s\ndx = %s"
    DUW = "Dimension unit has to be compatible to 'm'!"

    def __init__(self, image):
        assert image.unit == 1
        dims = image.dimensions
        assert dims[0].unit == dims[1].unit, self.NODNS
        dy, dx = [dim.data[1] - dim.data[0] for dim in dims]
        assert almost(dy, dx), self.DXDY % (dy.__repr__(), dx.__repr__())
        gunit = dims[0].unit ** -1
        aunit = (dy * dims[0].unit) ** 2
        funit = gunit / aunit
        self.gmul = gunit / self.GQUANT
        self.amul = aunit / self.AQUANT
        self.fmul = funit / self.FQUANT
        assert isinstance(self.gmul, float), DUW
        assert isinstance(self.amul, float), DUW
        assert isinstance(self.fmul, float), DUW


class Inclusion(object):
    TWO_TIMES_SQRT_ONE_OVER_PI = 1.1283791670

    def __init__(self, slices, focus, area):
        self.slices = slices
        self.focus = focus
        self.area = area
        self.valid = True

    def get_diameter(self):
        return self.TWO_TIMES_SQRT_ONE_OVER_PI \
               * (self.area * ZSUnits.AQUANT).sqrt()

    def get_info(self, zvalue, zind, label, dims):
        coordZ = zvalue
        yind = (self.slices[0].start + self.slices[0].stop - 1) / 2
        coordY = dims[0].data[yind] * dims[0].unit
        xind = (self.slices[1].start + self.slices[1].stop - 1) / 2
        coordX = dims[1].data[xind] * dims[1].unit
        return (coordZ, coordY, coordX, self.get_diameter(),
                self.focus * ZSUnits.FQUANT, label, zind,
                self.slices[0].start, self.slices[0].stop,
                self.slices[1].start, self.slices[1].stop)


class InvalidInclusion(object):
    valid = False
    focus = 0.0


class ZSParams(object):
    def __init__(self, worker):
        self.gth = Quantity(
            worker.paramGradientThreshold.value).inUnitsOf(ZSUnits.GUNIT).value
        self.ath = Quantity(
            worker.paramAreaThreshold.value).inUnitsOf(ZSUnits.AUNIT).value
        self.fth = Quantity(
            worker.paramFocusThreshold.value).inUnitsOf(ZSUnits.FUNIT).value
        self.grow = int(worker.paramGrow.value)
        self.connectivity = int(worker.paramConnectivity.value)


class AutoFocus(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "AutoFocus"
    _sockets = [("zstack", Connectors.TYPE_ARRAY)]
    _params = [("gradientThreshold", "Gradient threshold",
                "8.0 mum**-1", None),
               ("connectivity", "Connectivity for labels", 2, None),
               ("areaThreshold", "Area threshold", "16.0 mum**2", None),
               ("grow", "Measure focus at larger slices", 2, None),
               ("focusThreshold", "Focus threshold", "1.8 mum**-3", None),
               ("permanent", "Store results permanently", False, None)]
    from pyphant.core.KnowledgeManager import KnowledgeManager
    kmanager = KnowledgeManager.getInstance()

    def invalidate_unfocused(self, inclusions):
        if len(inclusions) <= 1:
            return
        inclusions.sort(key=lambda x: x.focus)
        max_focus = inclusions[-1].focus
        for inc in inclusions[:-1]:
            inc.valid = False
            inc.focus = max_focus

    def get_label_data(self, grad_data, zsp, zsu):
        thresh_data = numpy.where(grad_data < zsp.gth / zsu.gmul, False, True)
        fill_data = ndimage.binary_fill_holes(thresh_data)
        structure = ndimage.morphology.generate_binary_structure(
            fill_data.ndim, zsp.connectivity)
        return ndimage.label(fill_data, structure=structure)[0]

    def autofocus(self, image, zsp, zind, inclusions, last_label):
        zsu = ZSUnits(image)
        grad_data = numpy.sqrt(sum(numpy.square(
            numpy.array(numpy.gradient(image.data)))))
        label_data = self.get_label_data(grad_data, zsp, zsu)
        slicess = ndimage.find_objects(label_data)
        focus_data = numpy.zeros(grad_data.shape)
        inclusions[zind] = {}
        for label, slices in enumerate(slicess, start=1):
            bigslices = [slice(max(sli.start - zsp.grow, 0),
                               sli.stop + zsp.grow) for sli in slices]
            bigdetail = grad_data[bigslices]
            focus = bigdetail.sum() / bigdetail.size * zsu.fmul
            if focus < zsp.fth:
                inclusions[zind][label] = InvalidInclusion()
                continue
            islabel = (label_data[slices] == label)
            detail = numpy.where(islabel, True, False)
            eroded = ndimage.binary_erosion(detail)
            area = eroded.sum() * zsu.amul
            if area < zsp.ath:
                inclusions[zind][label] = InvalidInclusion()
                continue
            focus_data[slices] = numpy.where(islabel, focus,
                                             focus_data[slices])
            new_inclusion = Inclusion(slices, focus, area)
            if last_label is None:
                inclusions[zind][label] = new_inclusion
                continue
            last_detail = numpy.where(islabel, last_label[slices], 0)
            ld_labels = numpy.unique(last_detail)[1:]
            ld_inclusions = [inclusions[zind - 1][ld_label] \
                             for ld_label in ld_labels]
            ld_inclusions.append(new_inclusion)
            self.invalidate_unfocused(ld_inclusions)
            inclusions[zind][label] = new_inclusion
        return focus_data, label_data

    def make_fc(self, prototype, data, unit, prefix="",
                shortname=None, attributes={}, emd5_list=[]):
        longname = prefix + prototype.longname
        if shortname is None:
            shortname = prototype.shortname
        from copy import deepcopy
        dimensions = prototype.dimensions
        all_attributes = deepcopy(prototype.attributes)
        all_attributes.update(attributes)
        if all_attributes.has_key('vmin'):
            all_attributes.pop('vmin')
        if all_attributes.has_key('vmax'):
            all_attributes.pop('vmax')
        fc = FieldContainer(data=data, unit=unit, dimensions=dimensions,
                            longname=longname,
                            shortname=shortname, attributes=all_attributes)
        fc.seal()
        self.kmanager.registerDataContainer(
            fc, temporary=not self.paramPermanent.value)
        emd5_list.append(fc.id)

    def make_sc(self, column_data, longnames, shortnames, longname, shortname,
                attributes={}):
        unzipped = zip(*column_data)
        assert len(unzipped) == len(longnames) == len(shortnames)
        def get_column_fc(col, ln, sn):
            try:
                unit = Quantity(1.0, col[0].unit)
                data = [quant.value for quant in col]
            except (KeyError, AttributeError):
                unit = 1
                data = col
            from numpy import array
            fc = FieldContainer(data=array(data), unit=unit,
                                longname=ln, shortname=sn)
            fc.seal()
            self.kmanager.registerDataContainer(
                fc, temporary=not self.paramPermanent.value)
            return fc
        columns = [get_column_fc(col, ln, sn) for col, ln, sn \
                   in zip(unzipped, longnames, shortnames)]
        sc = SampleContainer(longname=longname, shortname=shortname,
                             attributes=attributes, columns=columns)
        sc.seal()
        self.kmanager.registerDataContainer(
            sc, temporary=not self.paramPermanent.value)
        return sc

    def get_attributes(self, zstype, applied_to):
        attributes = dict([(name, param.value) for name, param \
                           in self._params.iteritems() if name != 'name'])
        attributes.update({'ZStackType':zstype, 'applied_to':applied_to})
        return attributes

    def get_scs(self, zstack, subscriber=0):
        # Initialization:
        label_data = None
        inclusions = {}
        focused_inclusions = []
        sharp_iters = len(zstack['emd5'].data)
        focus_fcs = []
        label_fcs = []
        zsp = ZSParams(self)
        dimss = {}
        zvals = []
        # Calculate autofocus results:
        for zid, emd5 in enumerate(zstack['emd5'].data):
            raw_image = self.kmanager.getDataContainer(emd5)
            dimss[zid] = raw_image.dimensions
            focus_data, label_data = self.autofocus(
                raw_image, zsp, zid, inclusions, label_data)
            cdata = [[raw_image, focus_data, ZSUnits.FQUANT, 'Focus_', 'f',
                      self.get_attributes('FocusImage', zstack.id), focus_fcs],
                     [raw_image, label_data, 1, 'Label_', 'l',
                      self.get_attributes('LabelImage', zstack.id), label_fcs]]
            for data in cdata:
                self.make_fc(*data)
            subscriber %= ((zid + 1) * 90) / sharp_iters
        # Extract statistics:
        for zind, inc_dict in inclusions.iteritems():
            zvalue = zstack['z-value'].data[zind] * zstack['z-value'].unit
            zvals.append(zvalue)
            for label, inclusion in inc_dict.iteritems():
                if inclusion.valid:
                    info = inclusion.get_info(zvalue, zind, label, dimss[zind])
                    focused_inclusions.append(info)
            subscriber %= 90 + ((zind + 1) * 10) / sharp_iters
        # Put all results into SampleContainers:
        columnss = [zip(zvals, focus_fcs), zip(zvals, label_fcs),
                    focused_inclusions]
        columnlnss = [['z-value', 'emd5'], ['z-value', 'emd5'],
                      ['z-pos', 'y-pos', 'x-pos', 'diameter',
                       'focus', 'label', 'z-index',
                       'y-slice-start', 'y-slice-stop',
                       'x-slice-start', 'x-slice-stop']]
        columnsnss = [['z', 'e'], ['z', 'e'],
                      ['z', 'y', 'x', 'd', 'f', 'l',
                        'zi', 'yt', 'yp', 'xt', 'xp']]
        longnames = ['Focus_' + zstack.longname, 'Label_' + zstack.longname,
                     "Statistics_" + zstack.longname]
        shortnames = ['f', 'l', 's']
        attributess = [self.get_attributes(zstype, zstack.id) \
                       for zstype in ['FocusSC', 'LabelSC', 'StatisticsSC']]
        return [self.make_sc(*data) for data in \
                zip(columnss, columnlnss, columnsnss,
                    longnames, shortnames, attributess)]

    def validateSC(self, emd5SC):
        if emd5SC.attributes['ZStackType'] == 'StatisticsSC':
            return True
        for emd5 in emd5SC['emd5'].data:
            if not self.kmanager.hasDataContainer(str(emd5)):
                self.kmanager.setTemporary(emd5SC.id, True)
                return False
        return True

    def lookup(self, zstype, emd5):
        search_dict = {'type':'sample',
                       'attributes':self.get_attributes(zstype, emd5)}
        result = self.kmanager.search(['id'], search_dict=search_dict)
        if len(result) == 0:
            return None
        else:
            for emd5inlist in result:
                emd5SC = self.kmanager.getDataContainer(emd5inlist[0])
                if self.validateSC(emd5SC):
                    return emd5SC
            return None #<- ugly case: FCs saved temp., but SC saved in Recipe

    def get_result_sc(self, zstack, zstype, index, subscriber=0):
        lookup = self.lookup(zstype, zstack.id)
        if lookup is None:
            return self.get_scs(zstack, subscriber)[index]
        else:
            return lookup

    @Worker.plug(Connectors.TYPE_ARRAY)
    def get_focus_sc(self, zstack, subscriber=0):
        return self.get_result_sc(zstack, 'FocusSC', 0, subscriber)

    @Worker.plug(Connectors.TYPE_ARRAY)
    def get_label_sc(self, zstack, subscriber=0):
        return self.get_result_sc(zstack, 'LabelSC', 1, subscriber)

    @Worker.plug(Connectors.TYPE_ARRAY)
    def get_statistics_sc(self, zstack, subscriber=0):
        return self.get_result_sc(zstack, 'StatisticsSC', 2, subscriber)
