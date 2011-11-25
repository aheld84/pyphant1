# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009-2011, Andreas W. Liehr (liehr@users.sourceforge.net)
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

import mx.DateTime.ISO
from pyphant.quantities import Quantity
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity

import logging
_logger = logging.getLogger("pyphant")

def str2unit(unitStr,FMFversion='1.1'):
    """The function str2unit is a factory, which either returns a float or a Quantity instance from a given string. Because the definition of units and physical constants is not unique for 
    FMFversion 1.0 (http://arxiv.org/abs/0904.1299) and 
    FMFversion 1.1 (http://dx.doi.org/10.1016/j.cpc.2009.11.014), the result of str2unit() depends on FMFversion.
    """
    if FMFversion not in ['1.0','1.1']:
        raise ValueError, 'FMFversion %s not supported.' % FMFversion

    # Deal with exceptional units like '%' or 'a.u.'
    if unitStr.endswith('%'):
        if len(unitStr.strip()) == 1:
            return 0.01
        else:
            return float(unitStr[:-1])/100.0
    elif unitStr.endswith('a.u.'):
        if len(unitStr.strip()) == 4:
            return 1.0
        else:
            return float(unitStr[:-4])

    # Prepare conversion to quantity
    if unitStr.startswith('.'):
        unitStr = '0'+unitStr
    elif not (unitStr[0].isdigit() or unitStr[0]=='-'):
        unitStr = '1'+unitStr
    # Convert input to quantity or float
    if FMFversion not in ['1.0','1.1']:
        raise ValueError, 'FMFversion %s not supported.' % FMFversion
    else:
        unitStr = unitStr.replace('^', '**')
        try: #FMFversion=='1.1'
            unit = Quantity(unitStr.encode('utf-8'))
        except:
            unit = None

        if FMFversion=='1.0':
            try:
                unit1_0 = PhysicalQuantity(unitStr.encode('utf-8'))
                unit1_1 = Quantity(str(unit1_0.inBaseUnits()))
            except:
                unit1_1 = None
            
            if isinstance(unit1_1,Quantity): # Unit exists in 1.0
                if isinstance(unit,Quantity): # Unit also exists in 1.1
                    if unit.isCompatible(unit1_1.unit): # Interpretation of unit has not changed
                        unit = unit1_1.inUnitsOf(unit.unit)
                    else:
                        unit = unit1_1
                        _logger.warn('Usage of old unit "%s" required '
                                     'conversion to base units.' % unitStr)
                else:
                    unit = unit1_1
                    _logger.warn('Usage of old unit "%s" required '
                                 'conversion to base units.' % unitStr)
                
        if unit == None:
            try:
                if 'j' in unitStr:
                    unit = complex(unitStr)
                else:
                    unit = float(unitStr)
            except:
                raise ValueError, "Unit %s cannot be interpreted." % unitStr
    return unit
        
def parseQuantity(value,FMFversion='1.1'):
    import re
    pm = re.compile(ur"(?:\\pm|\+-|\+/-)")
    try:
        value, error = [s.strip() for s in pm.split(value)]
    except:
        error = None
    if value.startswith('('):
        value = float(value[1:])
        error, unit = [s.strip() for s in error.split(')')]
        unit = str2unit(unit,FMFversion)
        value *= unit
    else:
        value = str2unit(value,FMFversion)
    if error != None:
        if error.endswith('%'):
            error = value*float(error[:-1])/100.0
        else:
            try:
                error = float(error)*unit
            except:
                error = str2unit(error,FMFversion)
    return value, error

def parseVariable(oldVal,FMFversion='1.1'):
    shortname, value = tuple([s.strip() for s in oldVal.split('=')])
    value, error = parseQuantity(value,FMFversion)
    return (shortname, value, error)

def parseDateTime(value,FMFversion='1.1'):
    """
    >>>parseDateTime('2004-08-21 12:00:00+-12hr')
    (Quantity(731814.5,'d'), Quantity(0.5,'d'))
    >>>parseDateTime('2004-08-21 12:00:00')
    (Quantity(731814.5,'d'), None)
    """
    datetimeWithError = value.split('+-')
    if len(datetimeWithError)==2:
        datetime = mx.DateTime.ISO.ParseAny(datetimeWithError[0])
        uncertainty = parseQuantity(datetimeWithError[1],FMFversion)[0]
        if uncertainty.isCompatible('h'):
            _logger.warning("The uncertainty of timestamp %s has the unit 'h', which is deprecated. The correct abbreviation for hour is 'hr'." % value)
            uncertainty = uncertainty*Quantity('1hr/h')
        error = uncertainty.inUnitsOf('d')
    else:
        datetime = mx.DateTime.ISO.ParseAny(value)
        error = None
    days,seconds = datetime.absvalues()
    return (Quantity(days,'d')+Quantity(seconds,'s'),error)
