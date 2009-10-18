# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
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

u"""
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from PhysicalQuantities import Quantity
import mx.DateTime.ISO

def str2unit(unit):
    if unit.startswith('.'):
        unit = '0'+unit
    elif unit.endswith('%'):
        try:
            unit = float(unit[:-1])/100.0
        except: 
            unit = 0.01
    elif unit.endswith('a.u.'):
        try:
            unit = float(unit[:-4])
        except:
            unit = 1.0
    elif not (unit[0].isdigit() or unit[0]=='-'):
        unit = '1'+unit
    try:
        unit = unit.replace('^', '**')
        unit = Quantity(unit.encode('utf-8'))
    except:
        unit = float(unit)
    return unit

def parseQuantity(value):
    import re
    pm = re.compile(ur"(?:\\pm|\+-|\+/-)")
    try:
        value, error = [s.strip() for s in pm.split(value)]
    except:
        error = None
    if value.startswith('('):
        value = float(value[1:])
        error, unit = [s.strip() for s in error.split(')')]
        unit = str2unit(unit)
        value *= unit
    else:
        value = str2unit(value)
    if error != None:
        if error.endswith('%'):
            error = value*float(error[:-1])/100.0
        else:
            try:
                error = float(error)*unit
            except:
                error = str2unit(error)
    return value, error

def parseVariable(oldVal):
    shortname, value = tuple([s.strip() for s in oldVal.split('=')])
    value, error = parseQuantity(value)
    return (shortname, value, error)

def parseDateTime(value):
    """
    >>>parseDateTime('2004-08-21 12:00:00+-12h')
    (Quantity(731814.5,'d'), Quantity(0.5,'d'))
    >>>parseDateTime('2004-08-21 12:00:00')
    (Quantity(731814.5,'d'), None)
    """
    datetimeWithError = value.split('+-')
    if len(datetimeWithError)==2:
        datetime = mx.DateTime.ISO.ParseAny(datetimeWithError[0])
        error = parseQuantity(datetimeWithError[1])[0].inUnitsOf('d')
    else:
        datetime = mx.DateTime.ISO.ParseAny(value)
        error = None
    days,seconds = datetime.absvalues()
    return (Quantity(days,'d')+Quantity(seconds,'s'),error)
