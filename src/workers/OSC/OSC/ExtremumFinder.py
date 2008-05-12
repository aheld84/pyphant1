# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008, Rectorate of the University of Freiburg
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

u"""Pyphant module providing worker for finding the local extrema of 1D functions.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import numpy
from pyphant.core import (Worker, Connectors,
                          Param, DataContainer)

import scipy.interpolate
from Scientific.Physics import PhysicalQuantities
import copy

class ExtremumFinder(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Extremum Finder"

    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = [("extremum", u"extremum", [u"minima",u"maxima",u"both"], None)
               ]

    @Worker.plug(Connectors.TYPE_IMAGE)
    def locate(self, field, subscriber=0):
        extremaPos = []
        extremaError = []
        extremaCurv = []
        x = field.dimensions[-1].data
        dx   = numpy.diff(x)
        dyx  = 0.5*(x[:-1] + x[1:])
        if len(field.dimensions)==1:
            count = 1
        else:
            count = len(field.dimensions[0].data)
        for i in xrange(count):
            if count == 1:
                y = field.data
                Dy= field.error
            else:
                y = field.data[i]
                if field.error != None:
                    Dy= field.error[i]
                else:
                    Dy= field.error
            #compute first derivative
            dy   = numpy.diff(y)
            x0Pos= numpy.sign(dy[:-1])!=numpy.sign(dy[1:])
            x0 = []
            DeltaX = []
            dyy   = []
            if numpy.sometrue(x0Pos):
                index = numpy.extract(x0Pos,numpy.arange(len(dy)))
                skipOne = False
                for i in index:
                    if skipOne:
                        skipOne = False
                    else:
                        dyy.append(-numpy.sign(dy[i]))
                        if dy[i]==-dy[i+1]: #Exact minimum
                            x0.append(0.5*(dyx[i]+dyx[i+1]))
                            if field.error != None:
                                DeltaX.append(Dy[i])
                            else:
                                DeltaX.append(numpy.NaN)
                            skipOne = True
                        elif dy[i+1]==0: # Symmetrically boxed Error
                            x0.append(dyx[i+1])
                            if field.error != None:
                                DeltaX.append(Dy[i+1]+Dy[i+2])
                            else:
                                DeltaX.append(numpy.NaN)
                            skipOne = True
                        else:
                            extr=dyx[i]-(dyx[i+1]-dyx[i])/(dy[i+1]/dx[i+1]-dy[i]/dx[i])*dy[i]/dx[i]
                            x0.append(extr)
                            if field.error != None:
                                scale = 0.5*dx[i]*dx[i+1]*(x[i+2]-x[i])
                                scale/= (y[i]*dx[i+1]+y[i+1]*(x[i]-x[i+2])+y[i+2]*dx[i])**2
                                partError = scale * numpy.array([-dy[i+1],y[i+2]-y[i],-dy[i]])
                                DeltaX.append(numpy.dot(Dy[i:i+3],numpy.abs(partError)))
                            else:
                                DeltaX.append(numpy.NaN)
            else:
                x0.append(numpy.NaN)
                DeltaX.append(numpy.NaN)
            extremaPos.append(numpy.array(x0))
            extremaError.append(numpy.array(DeltaX))
            extremaCurv.append(numpy.array(dyy))
        #Map roots and curvatures to arrays
        if count == 1:
            X0 = numpy.array(x0)
            XCurv = numpy.array(extremaCurv[0])
            XError= numpy.array(extremaError[0])
        else:
            maxLen = max(map(len,extremaPos))
            X0 = numpy.zeros((count,maxLen),'f')
            X0[:] = numpy.NaN
            XCurv = X0.copy()
            XError= X0.copy()
            for i in xrange(count):
                numExt = len(extremaPos[i])
                if numExt == 1:
                    X0[i,0]=extremaPos[i][0]
                    XCurv[i,0]=extremaCurv[i][0]
                    XError[i,0]=extremaError[i][0]
                    # Last two lines above were:
                    # XCurv[i,0]=extremaCurv[i]
                    # XError[i,0]=extremaError[i]
                    # This is clearly illegal, but above patch is not semantically checked,
                    # though syntactically correct. This MUST be checked!
                else:
                    for j in xrange(numExt):
                        X0[i,j]=extremaPos[i][j]
                        XCurv[i,j]=extremaCurv[i][j]
                        XError[i,j]=extremaError[i][j]
        extremaType = self.paramExtremum.value
        if extremaType == u'minima':
            X0 = numpy.where(XCurv > 0,X0,numpy.nan)
            error = numpy.where(XCurv > 0,XError,numpy.nan)
        elif extremaType == u'maxima':
            X0 = numpy.where(XCurv < 0,X0,numpy.nan)
            error = numpy.where(XCurv < 0,XError,numpy.nan)
        else:
            extremaType = u'extrema'
            error = XError
        xName = field.dimensions[-1].longname
        xSym  = field.dimensions[-1].shortname
        yName = field.longname
        ySym  = field.shortname
        if numpy.sometrue(numpy.isnan(X0)):
            if len(field.dimensions) == 1:
                roots = DataContainer.FieldContainer(numpy.extract(numpy.logical_not(numpy.isnan(X0)),X0),
                                                 unit = field.dimensions[-1].unit,
                                                 longname="%s of the local %s of %s" % (xName,extremaType,yName),
                                                 shortname="%s_0" % xSym)
            else:
                roots = DataContainer.FieldContainer(X0.transpose(),
                                                 mask = numpy.isnan(X0).transpose(),
                                                 unit = field.dimensions[-1].unit,
                                                 longname="%s of the local %s of %s" % (xName,extremaType,yName),
                                                 shortname="%s_0" % xSym)
        else:
            roots = DataContainer.FieldContainer(X0.transpose(),
                                                 unit = field.dimensions[-1].unit,
                                                 longname="%s of the local %s of %s" % (xName,extremaType,yName),
                                                 shortname="%s_0" % xSym)
        if field.error != None:
            if len(field.dimensions)==1:
                roots.error = numpy.extract(numpy.logical_not(numpy.isnan(X0)),error)
            else:
                roots.error = error.transpose()
        else:
            roots.error = None
        if len(field.data.shape)==2:
            roots.dimensions[-1] = field.dimensions[0]
        roots.seal()
        return roots
