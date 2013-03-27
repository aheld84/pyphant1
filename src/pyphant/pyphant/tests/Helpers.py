# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
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

__version__ = "$Revision$"
# $Source$

import numpy

def fixedPoints(lambdaVec,kappa1=0.0):
    """Compute fixed points x0 and slope f'(x0) of f(x)=-lambda*x+x**3-kappa1."""
    #Compute constants, which do not depend on parameter lambda
    oneIsqrt3 = numpy.complex(1.0,numpy.sqrt(3.0))
    oneIMsqrt3 = numpy.complex(1.0,-numpy.sqrt(3.0))
    lambdaC = (float(abs(kappa1))/2)**(2.0/3.0)
    umCounter = (2.0/3.0)**(1.0/3.0)
    umDenominator = 2.0**(1.0/3.0)*3.0**(2.0/3.0)
    ulrDenominator = 2.0**(2.0/3.0)*3.0**(1.0/3.0)
    #Intialise lists of results
    mask = []
    x0 = []
    slope=[]
    #Loop over parameter lambda
    for lamb in lambdaVec:
        #Define function returning the slope for a given set of fixed points
        def computeSlope(u0):
            return -lamb + 3.0*u0**2
        #Compute constant, which does depend on parameter lambda
        R = (numpy.complex(-9.0,0.0)*kappa1+numpy.sqrt(3)*
             numpy.sqrt(numpy.complex(27.0,0.0)*kappa1**2-
                        numpy.complex(4.0,0.0)*lamb**3))**(1.0/3.0)
        #Compute fixed points of function f(x)=-lambda*x+x**3-kappa1
        um = -umCounter*lamb/R-R/umDenominator
        ul = oneIsqrt3*lamb/(ulrDenominator*R)+oneIMsqrt3*R/(2.0*umDenominator)
        ur = oneIMsqrt3*lamb/(ulrDenominator*R)+oneIsqrt3*R/(2.0*umDenominator)
        u0 = numpy.array([um,ul,ur])
        #Only real valued results reflect existing fixed points
        u01Pos = numpy.where(numpy.abs(numpy.imag(u0))<=1E-9,True,False)
        u0Real = numpy.real(u0[u01Pos])
        #Distuinguish between sub- and supercritical parameter ranges
        if len(u0Real)==1: #subcritical
            x0.append([u0Real[0],numpy.NaN,numpy.NaN])
            mask.append(numpy.array(map(lambda x: not x,[True,False,False])))
            slope.append(numpy.array([computeSlope(u0Real[0]),numpy.NaN,numpy.NaN]))
        else:#supercritical
            u0Sorted = numpy.sort(u0Real)
            x0.append(u0Sorted)
            mask.append(numpy.array(map(lambda x: not x,[True,True,True])))
            slope.append(numpy.array(map(computeSlope,u0Sorted)))
    return tuple(map(numpy.vstack, [x0,slope,mask]))
    #return x0,slope,mask
