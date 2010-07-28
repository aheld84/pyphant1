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
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors,
                          Param)
from pyphant.core.KnowledgeManager import KnowledgeManager
from pyphant.quantities import Quantity
import numpy


def estimate_vmin_vmax(zstack, statistics):
    zstype = zstack.attributes.get('ZStackType')
    if zstype == 'RawSC':
        return (0, 255)
    elif zstype == 'LabelSC':
        return (0, int(statistics['label'].data.max()))
    elif zstype == 'FocusSC':
        return (Quantity('0.0 mum**-3'),
                float(statistics['focus'].data.max()) \
                * statistics['focus'].unit)
    else:
        return None, None


class MarkAF(Worker.Worker):
    """
    TODO
    """
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "MarkAF"
    _SETMASK = 'Set mask according to focused slices'
    _CUTBUTLABELS = 'Cut everything but focused labels'
    _params = [('method', 'Method',
                [_SETMASK, _CUTBUTLABELS], None)]
    _sockets = [("zstack", Connectors.TYPE_ARRAY),
                ("statistics", Connectors.TYPE_ARRAY)]
    from pyphant.core.KnowledgeManager import KnowledgeManager
    kmanager = KnowledgeManager.getInstance()

    @Worker.plug(Connectors.TYPE_ARRAY)
    def getMarked(self, zstack, statistics, subscriber=0):
        method = self.paramMethod.value
        from copy import deepcopy
        output_sc = deepcopy(zstack)
        emd5s = []
        vmin, vmax = estimate_vmin_vmax(zstack, statistics)
        max_count = len(zstack['emd5'].data)
        for count, emd5 in enumerate(zstack['emd5'].data, start=1):
            image = self.kmanager.getDataContainer(emd5)
            if method == self._SETMASK:
                emd5s.append(self.getMarkedEmd5(image, statistics,
                                                vmin, vmax))
            elif method == self._CUTBUTLABELS:
                emd5s.append(self.getCutEmd5(image, statistics))
            subscriber %= (100 * count) / max_count
        output_sc['emd5'].data = numpy.array(emd5s)
        typename = {self._SETMASK:'Masked',
                    self._CUTBUTLABELS:'CutLabels'}[method]
        output_sc.longname = '%s_%s' % (typename, output_sc.longname)
        output_sc.shortname = 'm'
        output_sc.attributes.update({'ZStackType':'%sSC' % typename})
        output_sc.seal()
        return output_sc

    def getMarkedEmd5(self, image, statistics, vmin, vmax):
        from copy import deepcopy
        output_img = deepcopy(image)
        if vmin is not None:
            output_img.attributes.update({'vmin':vmin, 'vmax':vmax})
        mf_z = image.attributes['zid']
        slicess = [(slice(yt, yp), slice(xt, xp)) \
                   for yt, yp, xt, xp, z in zip(
            statistics['yt'].data, statistics['yp'].data,
            statistics['xt'].data, statistics['xp'].data,
            statistics['z-index'].data) if z == mf_z]
        mask = numpy.zeros(image.data.shape, dtype=bool)
        for slices in slicess:
            mask[slices] = True
        output_img.mask = mask
        output_img.seal()
        self.kmanager.registerDataContainer(output_img, temporary=True)
        return output_img.id

    def getCutEmd5(self, image, statistics):
        from copy import deepcopy
        output_img = deepcopy(image)
        output_img.data = numpy.zeros(image.data.shape,
                                      dtype=image.data.dtype)
        mf_z = image.attributes['zid']
        labelslicess = [(label, (slice(yt, yp), slice(xt, xp))) \
                       for label, yt, yp, xt, xp, z in zip(
            statistics['label'].data,
            statistics['yt'].data, statistics['yp'].data,
            statistics['xt'].data, statistics['xp'].data,
            statistics['z-index'].data) if z == mf_z]
        for labelslices in labelslicess:
            img_detail = image.data[labelslices[1]]
            output_detail = output_img.data[labelslices[1]]
            output_img.data[labelslices[1]] = numpy.where(
                 img_detail == labelslices[0],
                 img_detail, output_detail)
        output_img.seal()
        self.kmanager.registerDataContainer(output_img, temporary=True)
        return output_img.id
