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
"""

from pyphant.core import (Worker, Connectors)
import pkg_resources


class MarkInclusions(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution(
        "pyphant.imageprocessing"
        ).version
    name = "Mark Inclusions"
    _sockets = [("zstack", Connectors.TYPE_IMAGE),
                ("statistics", Connectors.TYPE_ARRAY)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def markInclusions(self, zstack, statistics, subscriber=0):
        from copy import deepcopy
        ret = deepcopy(zstack)
        ret.longname = "Marked_%s" % zstack.longname
        zst = zstack.attributes.get('ZStackType') or "unknown"
        ret.attributes['ZStackType'] = "Marked_%s" % zst
        s = statistics
        import numpy
        for zi, yt, yp, xt, xp in zip(s['zi'].data, s['yt'].data,
                                      s['yp'].data,
                                      s['xt'].data, s['xp'].data):
            slices = (slice(yt, yp), slice(xt, xp))
            border = numpy.ones((yp - yt, xp - xt), dtype=bool)
            try:
                border[(slice(2, yp - yt - 2),
                        slice(2, xp - xt - 2))] \
                        = numpy.zeros(((yp - yt) - 4, (xp - xt) - 4),
                                      dtype=bool)
            except (KeyError, ValueError):
                pass
            ret.data[zi][slices] = numpy.where(border, 255,
                                               ret.data[zi][slices])
        ret.seal()
        return ret
