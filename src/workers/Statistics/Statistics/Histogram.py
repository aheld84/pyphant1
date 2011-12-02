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
The Historgam Worker is a class of Pyphant's Statistic Toolbox. It
calcuates a histogram from the provided data. Histograms can be
visualisd as bar charts or line charts. The rexpective axes are
automatically correctly labled.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Connectors, DataContainer,
                          Worker)
import numpy

class Histogram(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Histogram"
    _sockets=[("vector", Connectors.TYPE_IMAGE)]
    _params = [("bins", "Bins", 10, None)]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def calculateHistogram(self, vector, subscriber=0):
        bins = self.paramBins.value
        assert bins >= 2
        # numpy 1.3
        try:
            histo = numpy.histogram(vector.data.flat, bins, new=True,
                                    range=(numpy.floor(vector.data.min()),
                                           numpy.ceil(vector.data.max())))
        # newer numpy versions
        except TypeError:
            histo = numpy.histogram(vector.data.flat, bins,
                                    range=(numpy.floor(vector.data.min()),
                                           numpy.ceil(vector.data.max())))
        binCenters = histo[1][:-1] + (numpy.diff(histo[1]) / 2.0)
        assert len(binCenters) == bins == len(histo[0])
        xdim = DataContainer.FieldContainer(binCenters, vector.unit,
                                            longname=vector.longname,
                                            shortname=vector.shortname)
        result = DataContainer.FieldContainer(histo[0], dimensions=[xdim],
                                              longname=u"Histogram of %s"
                                              % vector.longname,
                                              shortname=u"h")
        result.seal()
        return result
