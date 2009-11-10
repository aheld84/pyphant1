# -*- coding: utf-8 -*-

# Copyright (c) 1998-2007, Konrad Hinsen <hinsen@cnrs-orleans.fr>
# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr
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
Quantities with units

based on the module Scientific.Physics.PhysicalQuantities
written by Conrad Hinsen with contributions from Greg Ward.

This module provides a data type that represents a physical
quantity together with its unit. It is possible to add and
subtract these quantities if the units are compatible, and
a quantity can be converted to another compatible unit.
Multiplication, subtraction, and raising to integer powers
is allowed without restriction, and the result will have
the correct unit. A quantity can be raised to a non-integer
power only if the result can be represented by integer powers
of the base units.

The values of physical constants are taken from the 1986
recommended values from CODATA. Other conversion factors
(e.g. for British units) come from various sources. I can't
guarantee for the correctness of all entries in the unit
table, so use this at your own risk.
"""

rc = { 'fetchCurrencyRates' : False }

class NumberDict(dict):

    """
    Dictionary storing numerical values

    Constructor: NumberDict()

    An instance of this class acts like an array of number with
    generalized (non-integer) indices. A value of zero is assumed
    for undefined entries. NumberDict instances support addition,
    and subtraction with other NumberDict instances, and multiplication
    and division by scalars.
    """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return 0

    def __coerce__(self, other):
        if type(other) == type({}):
            other = NumberDict(other)
        return self, other

    def __add__(self, other):
        sum_dict = NumberDict()
        for key in self.keys():
            sum_dict[key] = self[key]
        for key in other.keys():
            sum_dict[key] = sum_dict[key] + other[key]
        return sum_dict

    def __sub__(self, other):
        sum_dict = NumberDict()
        for key in self.keys():
            sum_dict[key] = self[key]
        for key in other.keys():
            sum_dict[key] = sum_dict[key] - other[key]
        return sum_dict

    def __mul__(self, other):
        new = NumberDict()
        for key in self.keys():
            new[key] = other*self[key]
        return new
    __rmul__ = __mul__

    def __div__(self, other):
        new = NumberDict()
        for key in self.keys():
            new[key] = self[key]/other
        return new

import numpy.oldnumeric
def int_sum(a, axis=0):
    return numpy.oldnumeric.add.reduce(a, axis)
def zeros_st(shape, other):
    return numpy.oldnumeric.zeros(shape, dtype=other.dtype)
from numpy import ndarray as array_type


import re, string


# Class definitions

class Quantity:

    """
    Quantity with units

    Quantity instances allow addition, subtraction,
    multiplication, and division with each other as well as
    multiplication, division, and exponentiation with numbers.
    Addition and subtraction check that the units of the two operands
    are compatible and return the result in the units of the first
    operand. A limited set of mathematical functions (from module
    Numeric) is applicable as well:

      - sqrt: equivalent to exponentiation with 0.5.

      - sin, cos, tan: applicable only to objects whose unit is
        compatible with 'rad'.

    See the documentation of the Quantities module for a list
    of the available units.

    Here is an example on usage:

    >>> from quantities import Quantity as p  # short hand
    >>> distance1 = p('10 m')
    >>> distance2 = p('10 km')
    >>> total = distance1 + distance2
    >>> total
    Quantity(10010.0,'m')
    >>> total.convertToUnit('km')
    >>> total.getValue()
    10.01
    >>> total.getUnitName()
    'km'
    >>> total = total.inBaseUnits()
    >>> total
    Quantity(10010.0,'m')
    >>>
    >>> t = p(314159., 's')
    >>> # convert to days, hours, minutes, and second:
    >>> t2 = t.inUnitsOf('d','hr','min','s')
    >>> t2_print = ' '.join([str(i) for i in t2])
    >>> t2_print
    '3.0 d 15.0 h 15.0 min 59.0 s'
    >>>
    >>> e = p('2.7 Hartree*Nav')
    >>> e.convertToUnit('kcal/mol')
    >>> e
    Quantity(1694.2757596034764,'kcal/mol')
    >>> e = e.inBaseUnits()
    >>> str(e)
    '7088849.77818 kg*m**2/s**2/mol'
    >>>
    >>> freeze = p('0 degC')
    >>> freeze = freeze.inUnitsOf ('degF')
    >>> str(freeze)
    '32.0 degF'
    >>>
    """

    def __init__(self, *args):
        """
        There are two constructor calling patterns:

            1. Quantity(value, unit), where value is any number
            and unit is a string defining the unit

            2. Quantity(value_with_unit), where value_with_unit
            is a string that contains both the value and the unit,
            i.e. '1.5 m/s'. This form is provided for more convenient
            interactive use.

        @param args: either (value, unit) or (value_with_unit,)
        @type args: (number, C{str}) or (C{str},)
        """
        if len(args) == 2:
            self.value = args[0]
            self.unit = _findUnit(args[1])
        else:
            s = string.strip(args[0])
            match = Quantity._number.match(s)
            if match is None:
                raise TypeError('No number found')
            self.value = string.atof(match.group(0))
            self.unit = _findUnit(s[len(match.group(0)):])

    _number = re.compile('[+-]?[0-9]+(\\.[0-9]*)?([eE][+-]?[0-9]+)?')

    def __str__(self):
        return str(self.value) + ' ' + self.unit.name()

    def __repr__(self):
        return (self.__class__.__name__ + '(' + `self.value` + ',' +
                `self.unit.name()` + ')')

    def _sum(self, other, sign1, sign2):
        if not isQuantity(other):
            raise TypeError('Incompatible types')
        new_value = sign1*self.value + \
                    sign2*other.value*other.unit.conversionFactorTo(self.unit)
        return self.__class__(new_value, self.unit)

    def __add__(self, other):
        return self._sum(other, 1, 1)

    __radd__ = __add__

    def __sub__(self, other):
        return self._sum(other, 1, -1)

    def __rsub__(self, other):
        return self._sum(other, -1, 1)

    def __cmp__(self, other):
        diff = self._sum(other, 1, -1)
        return cmp(diff.value, 0)

    def __mul__(self, other):
        if not isQuantity(other):
            return self.__class__(self.value*other, self.unit)
        value = self.value*other.value
        unit = self.unit*other.unit
        if unit.isDimensionless():
            return value*unit.factor
        else:
            return self.__class__(value, unit)

    __rmul__ = __mul__

    def __div__(self, other):
        if not isQuantity(other):
            return self.__class__(self.value/other, self.unit)
        value = self.value/other.value
        unit = self.unit/other.unit
        if unit.isDimensionless():
            return value*unit.factor
        else:
            return self.__class__(value, unit)

    def __rdiv__(self, other):
        if not isQuantity(other):
            return self.__class__(other/self.value, pow(self.unit, -1))
        value = other.value/self.value
        unit = other.unit/self.unit
        if unit.isDimensionless():
            return value*unit.factor
        else:
            return self.__class__(value, unit)

    def __pow__(self, other):
        if isQuantity(other):
            raise TypeError('Exponents must be dimensionless')
        return self.__class__(pow(self.value, other), pow(self.unit, other))

    def __rpow__(self, other):
        raise TypeError('Exponents must be dimensionless')

    def __abs__(self):
        return self.__class__(abs(self.value), self.unit)

    def __pos__(self):
        return self

    def __neg__(self):
        return self.__class__(-self.value, self.unit)

    def __nonzero__(self):
        return self.value != 0

    def convertToUnit(self, unit):
        """
        Change the unit and adjust the value such that
        the combination is equivalent to the original one. The new unit
        must be compatible with the previous unit of the object.

        @param unit: a unit
        @type unit: C{str}
        @raise TypeError: if the unit string is not a know unit or a
        unit incompatible with the current one
        """
        unit = _findUnit(unit)
        self.value = _convertValue (self.value, self.unit, unit)
        self.unit = unit

    def inUnitsOf(self, *units):
        """
        Express the quantity in different units. If one unit is
        specified, a new Quantity object is returned that
        expresses the quantity in that unit. If several units
        are specified, the return value is a tuple of
        PhysicalObject instances with with one element per unit such
        that the sum of all quantities in the tuple equals the the
        original quantity and all the values except for the last one
        are integers. This is used to convert to irregular unit
        systems like hour/minute/second.

        @param units: one or several units
        @type units: C{str} or sequence of C{str}
        @returns: one or more physical quantities
        @rtype: L{Quantity} or C{tuple} of L{Quantity}
        @raises TypeError: if any of the specified units are not compatible
        with the original unit
        """
        units = map(_findUnit, units)
        if len(units) == 1:
            unit = units[0]
            value = _convertValue (self.value, self.unit, unit)
            return self.__class__(value, unit)
        else:
            units.sort()
            result = []
            value = self.value
            unit = self.unit
            for i in range(len(units)-1,-1,-1):
                value = value*unit.conversionFactorTo(units[i])
                if i == 0:
                    rounded = value
                else:
                    rounded = _round(value)
                result.append(self.__class__(rounded, units[i]))
                value = value - rounded
                unit = units[i]
            return tuple(result)

    # Contributed by Berthold Hoellmann
    def inBaseUnits(self):
        """
        @returns: the same quantity converted to base units,
        i.e. SI units in most cases
        @rtype: L{Quantity}
        """
        new_value = self.value * self.unit.factor
        num = ''
        denom = ''
        for i in xrange(9):
            unit = _base_names[i]
            power = self.unit.powers[i]
            if power < 0:
                denom = denom + '/' + unit
                if power < -1:
                    denom = denom + '**' + str(-power)
            elif power > 0:
                num = num + '*' + unit
                if power > 1:
                    num = num + '**' + str(power)
        if len(num) == 0:
            num = '1'
        else:
            num = num[1:]
        return self.__class__(new_value, num + denom)

    def isCompatible (self, unit):
        """
        @param unit: a unit
        @type unit: C{str}
        @returns: C{True} if the specified unit is compatible with the
        one of the quantity
        @rtype: C{bool}
        """
        unit = _findUnit (unit)
        return self.unit.isCompatible (unit)

    def getValue(self):
        """Return value (float) of physical quantity (no unit)."""
        return self.value

    def getUnitName(self):
        """Return unit (string) of physical quantity."""
        return self.unit.name()

    def sqrt(self):
        return pow(self, 0.5)

    def sin(self):
        if self.unit.isAngle():
            return numpy.oldnumeric.sin(self.value * \
                             self.unit.conversionFactorTo(_unit_table['rad']))
        else:
            raise TypeError('Argument of sin must be an angle')

    def cos(self):
        if self.unit.isAngle():
            return numpy.oldnumeric.cos(self.value * \
                             self.unit.conversionFactorTo(_unit_table['rad']))
        else:
            raise TypeError('Argument of cos must be an angle')

    def tan(self):
        if self.unit.isAngle():
            return numpy.oldnumeric.tan(self.value * \
                             self.unit.conversionFactorTo(_unit_table['rad']))
        else:
            raise TypeError('Argument of tan must be an angle')


class PhysicalUnit:

    """
    Physical unit

    A physical unit is defined by a name (possibly composite), a scaling
    factor, and the exponentials of each of the SI base units that enter into
    it. Units can be multiplied, divided, and raised to integer powers.
    """

    def __init__(self, names, factor, powers, offset=0):
        """
        @param names: a dictionary mapping each name component to its
                      associated integer power (e.g. C{{'m': 1, 's': -1}})
                      for M{m/s}). As a shorthand, a string may be passed
                      which is assigned an implicit power 1.
        @type names: C{dict} or C{str}
        @param factor: a scaling factor
        @type factor: C{float}
        @param powers: the integer powers for each of the nine base units
        @type powers: C{list} of C{int}
        @param offset: an additive offset to the base unit (used only for
                       temperatures)
        @type offset: C{float}
        """
        if type(names) == type(''):
            self.names = NumberDict()
            self.names[names] = 1
        else:
            self.names = names
        self.factor = factor
        self.offset = offset
        self.powers = powers

    def __repr__(self):
        return '<PhysicalUnit ' + self.name() + '>'

    __str__ = __repr__

    def __cmp__(self, other):
        if self.powers != other.powers:
            raise TypeError('Incompatible units')
        return cmp(self.factor, other.factor)

    def __mul__(self, other):
        if self.offset != 0 or (isUnit (other) and other.offset != 0):
            raise TypeError("cannot multiply units with non-zero offset")
        if isUnit(other):
            return PhysicalUnit(self.names+other.names,
                                self.factor*other.factor,
                                map(lambda a,b: a+b,
                                    self.powers, other.powers))
        else:
            return PhysicalUnit(self.names+{str(other): 1},
                                self.factor*other,
                                self.powers,
                                self.offset * other)

    __rmul__ = __mul__

    def __div__(self, other):
        if self.offset != 0 or (isUnit (other) and other.offset != 0):
            raise TypeError("cannot divide units with non-zero offset")
        if isUnit(other):
            return PhysicalUnit(self.names-other.names,
                                self.factor/other.factor,
                                map(lambda a,b: a-b,
                                    self.powers, other.powers))
        else:
            return PhysicalUnit(self.names+{str(other): -1},
                                self.factor/other, self.powers)

    def __rdiv__(self, other):
        if self.offset != 0 or (isUnit (other) and other.offset != 0):
            raise TypeError("cannot divide units with non-zero offset")
        if isUnit(other):
            return PhysicalUnit(other.names-self.names,
                                other.factor/self.factor,
                                map(lambda a,b: a-b,
                                    other.powers, self.powers))
        else:
            return PhysicalUnit({str(other): 1}-self.names,
                                other/self.factor,
                                map(lambda x: -x, self.powers))

    def __pow__(self, other):
        if self.offset != 0:
            raise TypeError("cannot exponentiate units with non-zero offset")
        if isinstance(other, int):
            return PhysicalUnit(other*self.names, pow(self.factor, other),
                                map(lambda x,p=other: x*p, self.powers))
        if isinstance(other, float):
            inv_exp = 1./other
            rounded = int(numpy.oldnumeric.floor(inv_exp+0.5))
            if abs(inv_exp-rounded) < 1.e-10:
                if reduce(lambda a, b: a and b,
                          map(lambda x, e=rounded: x%e == 0, self.powers)):
                    f = pow(self.factor, other)
                    p = map(lambda x,p=rounded: x/p, self.powers)
                    if reduce(lambda a, b: a and b,
                              map(lambda x, e=rounded: x%e == 0,
                                  self.names.values())):
                        names = self.names/rounded
                    else:
                        names = NumberDict()
                        if f != 1.:
                            names[str(f)] = 1
                        for i in range(len(p)):
                            names[_base_names[i]] = p[i]
                    return PhysicalUnit(names, f, p)
                else:
                    raise TypeError('Illegal exponent')
        raise TypeError('Only integer and inverse integer exponents allowed')

    def conversionFactorTo(self, other):
        """
        @param other: another unit
        @type other: L{PhysicalUnit}
        @returns: the conversion factor from this unit to another unit
        @rtype: C{float}
        @raises TypeError: if the units are not compatible
        """
        if self.powers != other.powers:
            raise TypeError('Incompatible units')
        if self.offset != other.offset and self.factor != other.factor:
            raise TypeError(('Unit conversion (%s to %s) cannot be expressed ' +
                             'as a simple multiplicative factor') % \
                             (self.name(), other.name()))
        return self.factor/other.factor

    def conversionTupleTo(self, other): # added 1998/09/29 GPW
        """
        @param other: another unit
        @type other: L{PhysicalUnit}
        @returns: the conversion factor and offset from this unit to
                  another unit
        @rtype: (C{float}, C{float})
        @raises TypeError: if the units are not compatible
        """
        if self.powers != other.powers:
            raise TypeError('Incompatible units')

        # let (s1,d1) be the conversion tuple from 'self' to base units
        #   (ie. (x+d1)*s1 converts a value x from 'self' to base units,
        #   and (x/s1)-d1 converts x from base to 'self' units)
        # and (s2,d2) be the conversion tuple from 'other' to base units
        # then we want to compute the conversion tuple (S,D) from
        #   'self' to 'other' such that (x+D)*S converts x from 'self'
        #   units to 'other' units
        # the formula to convert x from 'self' to 'other' units via the
        #   base units is (by definition of the conversion tuples):
        #     ( ((x+d1)*s1) / s2 ) - d2
        #   = ( (x+d1) * s1/s2) - d2
        #   = ( (x+d1) * s1/s2 ) - (d2*s2/s1) * s1/s2
        #   = ( (x+d1) - (d1*s2/s1) ) * s1/s2
        #   = (x + d1 - d2*s2/s1) * s1/s2
        # thus, D = d1 - d2*s2/s1 and S = s1/s2
        factor = self.factor / other.factor
        offset = self.offset - (other.offset * other.factor / self.factor)
        return (factor, offset)

    def isCompatible (self, other):     # added 1998/10/01 GPW
        """
        @param other: another unit
        @type other: L{PhysicalUnit}
        @returns: C{True} if the units are compatible, i.e. if the powers of
                  the base units are the same
        @rtype: C{bool}
        """
        return self.powers == other.powers

    def isDimensionless(self):
        return not reduce(lambda a,b: a or b, self.powers)

    def isAngle(self):
        return self.powers[7] == 1 and \
               reduce(lambda a,b: a + b, self.powers) == 1

    def setName(self, name):
        self.names = NumberDict()
        self.names[name] = 1

    def name(self):
        num = ''
        denom = ''
        for unit in self.names.keys():
            power = self.names[unit]
            if power < 0:
                denom = denom + '/' + unit
                if power < -1:
                    denom = denom + '**' + str(-power)
            elif power > 0:
                num = num + '*' + unit
                if power > 1:
                    num = num + '**' + str(power)
        if len(num) == 0:
            num = '1'
        else:
            num = num[1:]
        return num + denom


# Type checks

def isUnit(x):
    """
    @param x: an object
    @type x: any
    @returns: C{True} if x is a L{PhysicalUnit}
    @rtype: C{bool}
    """
    return hasattr(x, 'factor') and hasattr(x, 'powers')

def isQuantity(x):
    """
    @param x: an object
    @type x: any
    @returns: C{True} if x is a L{Quantity}
    @rtype: C{bool}
    """
    return hasattr(x, 'value') and hasattr(x, 'unit')


# Helper functions

def _findUnit(unit):
    if type(unit) == type(''):
        name = string.strip(unit)
        unit = eval(name, _unit_table)
        for cruft in ['__builtins__', '__args__']:
            try: del _unit_table[cruft]
            except: pass

    if not isUnit(unit):
        raise TypeError(str(unit) + ' is not a unit')
    return unit

def _round(x):
    if numpy.oldnumeric.greater(x, 0.):
        return numpy.oldnumeric.floor(x)
    else:
        return numpy.oldnumeric.ceil(x)


def _convertValue (value, src_unit, target_unit):
    (factor, offset) = src_unit.conversionTupleTo(target_unit)
    return (value + offset) * factor


# SI unit definitions

_base_names = ['m', 'kg', 's', 'A', 'K', 'mol', 'cd', 'rad', 'sr','EUR','bit','B']

_base_units = [('m',   PhysicalUnit('m',   1.,    [1,0,0,0,0,0,0,0,0,0,0])),
	       ('g',   PhysicalUnit('g',   0.001, [0,1,0,0,0,0,0,0,0,0,0])),
	       ('s',   PhysicalUnit('s',   1.,    [0,0,1,0,0,0,0,0,0,0,0])),
	       ('A',   PhysicalUnit('A',   1.,    [0,0,0,1,0,0,0,0,0,0,0])),
	       ('K',   PhysicalUnit('K',   1.,    [0,0,0,0,1,0,0,0,0,0,0])),
	       ('mol', PhysicalUnit('mol', 1.,    [0,0,0,0,0,1,0,0,0,0,0])),
	       ('cd',  PhysicalUnit('cd',  1.,    [0,0,0,0,0,0,1,0,0,0,0])),
	       ('rad', PhysicalUnit('rad', 1.,    [0,0,0,0,0,0,0,1,0,0,0])),
	       ('sr',  PhysicalUnit('sr',  1.,    [0,0,0,0,0,0,0,0,1,0,0])),
               ('EUR',  PhysicalUnit('EUR',  1.,  [0,0,0,0,0,0,0,0,0,1,0])),
               ('bit',  PhysicalUnit('bit',  1.,  [0,0,0,0,0,0,0,0,0,0,1])),
	       ]

_prefixes = [('Y',  1.e24),
             ('Z',  1.e21),
             ('E',  1.e18),
             ('P',  1.e15),
             ('T',  1.e12),
             ('G',  1.e9),
             ('M',  1.e6),
             ('k',  1.e3),
             ('h',  1.e2),
             ('da', 1.e1),
             ('d',  1.e-1),
             ('c',  1.e-2),
             ('m',  1.e-3),
             ('mu', 1.e-6),
             ('n',  1.e-9),
             ('p',  1.e-12),
             ('f',  1.e-15),
             ('a',  1.e-18),
             ('z',  1.e-21),
             ('y',  1.e-24),
             ]

_binaryUnits = ['bit','B']
_binaryPrefixes = [('Ei',  2**60),
             ('Pi',  2**50),
             ('Ti',  2**40),
             ('Gi',  2**30),
             ('Mi',  2**20),
             ('Ki',  2**10)
]             

_unit_table = {}

for unit in _base_units:
    _unit_table[unit[0]] = unit[1]

_help = []

def _addUnit(name, unit, comment=''):
    if _unit_table.has_key(name):
	raise KeyError, 'Unit ' + name + ' already defined'
    if comment:
        _help.append((name, comment, unit))
    if type(unit) == type(''):
	unit = eval(unit, _unit_table)
        for cruft in ['__builtins__', '__args__']:
            try: del _unit_table[cruft]
            except: pass
    unit.setName(name)
    _unit_table[name] = unit

def _addPrefixed(unit,prefixes=_prefixes):
    _help.append('Prefixed units for %s:' % unit)
    _prefixed_names = []
    if unit in ['EUR','bit','B']:
        validPrefixes = filter(lambda prefix: prefix[1]>=1000,prefixes) 
    else:
        validPrefixes = prefixes
    for prefix in validPrefixes:
	name = prefix[0] + unit
	_addUnit(name, prefix[1]*_unit_table[unit])
        _prefixed_names.append(name)
    _help.append(', '.join(_prefixed_names))

# Units with prefixes
_help.append('SI derived units; these automatically get prefixes:\n' + \
     ', '.join([prefix + ' (%.0E)' % value for prefix, value in _prefixes]) + \
             '\n')


_unit_table['kg'] = PhysicalUnit('kg',   1., [0,1,0,0,0,0,0,0,0,0,0])

_addUnit('Hz', '1/s', 'Hertz')
_addUnit('N', 'm*kg/s**2', 'Newton')
_addUnit('Pa', 'N/m**2', 'Pascal')
_addUnit('J', 'N*m', 'Joule')
_addUnit('W', 'J/s', 'Watt')
_addUnit('C', 's*A', 'Coulomb')
_addUnit('V', 'W/A', 'Volt')
_addUnit('F', 'C/V', 'Farad')
_addUnit('ohm', 'V/A', 'Ohm')
_addUnit('S', 'A/V', 'Siemens')
_addUnit('Wb', 'V*s', 'Weber')
_addUnit('T', 'Wb/m**2', 'Tesla')
_addUnit('H', 'Wb/A', 'Henry')
_addUnit('lm', 'cd*sr', 'Lumen')
_addUnit('lx', 'lm/m**2', 'Lux')
_addUnit('Bq', '1/s', 'Becquerel')
_addUnit('Gy', 'J/kg', 'Gray')
_addUnit('Sv', 'J/kg', 'Sievert')
_addUnit('B', '8*bit', 'Byte')

del _unit_table['kg']

for unit in _unit_table.keys():
    _addPrefixed(unit)
for unit in _binaryUnits:
    _addPrefixed(unit,_binaryPrefixes)

# Fundamental constants
_help.append('Fundamental constants:')

_unit_table['pi'] = numpy.oldnumeric.pi
_addUnit('c', '299792458.*m/s', 'speed of light')
_addUnit('mu0', '4.e-7*pi*N/A**2', 'permeability of vacuum')
_addUnit('eps0', '1/mu0/c**2', 'permittivity of vacuum')
_addUnit('Fa','96485.3399*C/mol', 'Faraday constant')
_addUnit('G', '6.67428e-11*m**3/kg/s**2', 'gravitational constant')
_addUnit('h', '6.62606896e-34*J*s', 'Planck constant')
_addUnit('hbar', 'h/(2*pi)', 'Planck constant / 2pi')
_addUnit('e', '1.602176487e-19*C', 'elementary charge')
_addUnit('me', '9.10938215e-31*kg', 'electron mass')
_addUnit('mp', '1.672621637e-27*kg', 'proton mass')
_addUnit('Nav', '6.02214179e23/mol', 'Avogadro number')
_addUnit('k', '1.3806504e-23*J/K', 'Boltzmann constant')
_addUnit('Ryd','10973731.568527/m','Rydberg constant')

# Time units
_help.append('Time units:')

_addUnit('min', '60*s', 'minute')
_addUnit('hr', '60*min', 'hour')
_addUnit('d', '24*hr', 'day')
_addUnit('wk', '7*d', 'week')
_addUnit('yr', '365.25*d', 'year')

# Length units
_help.append('Length units:')

_addUnit('inch', '2.54*cm', 'inch')
_addUnit('ft', '12*inch', 'foot')
_addUnit('yd', '3*ft', 'yard')
_addUnit('mi', '5280.*ft', '(British) mile')
_addUnit('nmi', '1852.*m', 'Nautical mile')
_addUnit('Ang', '1.e-10*m', 'Angstrom')
_addUnit('lyr', 'c*yr', 'light year')
_addUnit('AU', '149597870691*m', 'astronomical unit')
_addUnit('pc', '3.08567758128E16*m','parsec')
_addUnit('Bohr', '4*pi*eps0*hbar**2/me/e**2', 'Bohr radius')

# Area units
_help.append('Area units:')

_addUnit('ha', '10000*m**2', 'hectare')
_addUnit('acres', 'mi**2/640', 'acre')
_addUnit('b', '1.e-28*m', 'barn')

# Volume units
_help.append('Volume units:')

_addUnit('l', 'dm**3', 'liter')
_addUnit('dl', '0.1*l', 'deci liter')
_addUnit('cl', '0.01*l', 'centi liter')
_addUnit('ml', '0.001*l', 'milli liter')
_addUnit('tsp', '4.92892159375*ml', 'teaspoon')
_addUnit('tbsp', '3*tsp', 'tablespoon')
_addUnit('floz', '2*tbsp', 'fluid ounce')
_addUnit('cup', '8*floz', 'cup')
_addUnit('pt', '16*floz', 'pint')
_addUnit('qt', '2*pt', 'quart')
_addUnit('galUS', '4*qt', 'US gallon')
_addUnit('galUK', '4.54609*l', 'British gallon')

# Mass units
_help.append('Mass units:')

_addUnit('u', '1.660538782e-27*kg', 'atomic mass units')
_addUnit('oz', '28.349523125*g', 'ounce')
_addUnit('lb', '16*oz', 'pound')
_addUnit('ton', '2000*lb', 'ton')

# Concentration units
_help.append('Concentration units:')
_addUnit('M','mol/m**3','molar concentration')
_addUnit('mM','0.001*mol/m**3','millimolar')
_addUnit('muM','10**-6*mol/m**3','micromolar')

# Force units
_help.append('Force units:')

_addUnit('dyn', '1.e-5*N', 'dyne (cgs unit)')

# Energy units
_help.append('Energy units:')

_addUnit('erg', '1.e-7*J', 'erg (cgs unit)')
_addUnit('eV', 'e*V', 'electron volt')
_addUnit('Hartree', 'me*e**4/16/pi**2/eps0**2/hbar**2', 'Wavenumbers/inverse cm')
_addUnit('Ken', 'k*K', 'Kelvin as energy unit')
_addUnit('cal', '4.184*J', 'thermochemical calorie')
_addUnit('kcal', '1000*cal', 'thermochemical kilocalorie')
_addUnit('cali', '4.1868*J', 'international calorie')
_addUnit('kcali', '1000*cali', 'international kilocalorie')
_addUnit('Btu', '1055.05585262*J', 'British thermal unit')

_addPrefixed('eV')

# Power units
_help.append('Power units:')

_addUnit('hp', '745.7*W', 'horsepower')

# Pressure units
_help.append('Pressure units:')

_addUnit('bar', '1.e5*Pa', 'bar (cgs unit)')
_addUnit('dbar', '1.e4*Pa', 'dbar (cgs unit)')
_addUnit('mbar', '1.e2*Pa', 'mbar (cgs unit)')
_addUnit('atm', '101325.*Pa', 'standard atmosphere')
_addUnit('torr', 'atm/760', 'torr = mm of mercury')
_addUnit('psi', '6894.75729317*Pa', 'pounds per square inch')

# Angle units
_help.append('Angle units:')

_addUnit('deg', 'pi*rad/180', 'degrees')

_help.append('Temperature units:')
# Temperature units -- can't use the 'eval' trick that _addUnit provides
# for degC and degF because you can't add units
kelvin = _findUnit ('K')
_addUnit ('degR', '(5./9.)*K', 'degrees Rankine')
_addUnit ('degC', PhysicalUnit (None, 1.0, kelvin.powers, 273.15),
          'degrees Celcius')
_addUnit ('degF', PhysicalUnit (None, 5./9., kelvin.powers, 459.67),
          'degree Fahrenheit')
del kelvin

_help.append('Old European currencies:')
#Taken from http://www.xe.com/euro.php on 2008-11-05
_addUnit('ATS', 'EUR/13.7603' ,'Austria, Schilling')
_addUnit('BEF', 'EUR/40.3399' ,'Belgium, Franc')
_addUnit('CYP', 'EUR/0.585274','Cyprus, Pound')
_addUnit('DEM', 'EUR/1.95583' ,'Germany, Deutsche Mark')
_addUnit('ESP', 'EUR/166.386' ,'Spain, Peseta')
_addUnit('FIM', 'EUR/5.94573' ,'Finland, Markka')
_addUnit('FRF', 'EUR/5.94573' ,'France, Franc')
_addUnit('GRD', 'EUR/340.750' ,'Greece, Drachma')
_addUnit('IEP', 'EUR/0.787564','Ireland, Pound')
_addUnit('ITL', 'EUR/1936.27' ,'Italy, Lira')
_addUnit('LUF', 'EUR/40.3399' ,'Luxembourg, Franc')
_addUnit('MTL', 'EUR/0.429300','Malta, Lira')
_addUnit('NLG', 'EUR/2.20371' ,'The Netherlands, Guilder (also called Florin)')
_addUnit('PTE', 'EUR/200.482' ,'Portugal, Escudo')
_addUnit('SIT', 'EUR/239.640' ,'Slovenia, Tolar')
_addUnit('VAL', 'EUR/1936.27' ,'Vatican City, Lira')

#Get daily updated exchange rates
if rc['fetchCurrencyRates']:
    import urllib
    from xml.dom import minidom
    url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    currencyNames={'USD':'US dollar'  ,     'JPY':'Japanese yen',
                   'BGN':'Bulgarian lev'  , 'CZK':'Czech koruna',
                   'DKK':'Danish krone'  ,  'EEK':'Estonian kroon',
                   'GBP':'Pound sterling'  ,'HUF':'Hungarian forint',
                   'LTL':'Lithuanian litas','LVL':'Latvian lats',
                   'PLN':'Polish zloty',    'RON':'New Romanian leu',
                   'SEK':'Swedish krona',   'SKK':'Slovak koruna',
                   'CHF':'Swiss franc',     'ISK':'Icelandic krona',
                   'NOK':'Norwegian krone', 'HRK':'Croatian kuna',
                   'RUB':'Russian rouble',  'TRY':'New Turkish lira',
                   'AUD':'Australian dollar','BRL':'Brasilian real',
                   'CAD':'Canadian dollar', 'CNY':'Chinese yuan renminbi',
                   'HKD':'Hong Kong dollar','IDR':'Indonesian rupiah',
                   'KRW':'South Korean won','MXN':'Mexican peso',
                   'MYR':'Malaysian ringgit','NZD':'New Zealand dollar',
                   'PHP':'Philippine peso', 'SGD':'Singapore dollar',
                   'THB':'Thai baht',       'ZAR':'South African rand'}
    try:
        doc = minidom.parseString(urllib.urlopen(url).read())
        elements = doc.documentElement.getElementsByTagName('Cube')
        for element in elements[2:]:
            currency = element.getAttribute('currency').encode('utf8')
            _addUnit(currency,
                     'EUR/%s' % element.getAttribute('rate').encode('utf8'),
                     currencyNames[currency])
        print "Added exchange rate of %s for %s." % (elements[1].getAttribute('time'),
                                                     [ i.getAttribute('currency').encode('utf8')
                                                       for i in elements[2:] ])
    except:
        print "WARNING: No daily exchange rates available."

def description():
    """Return a string describing all available units."""
    s = ''  # collector for description text
    for entry in _help:
        if isinstance(entry, basestring):
            # headline for new section
            s += '\n' + entry + '\n'
        elif isinstance(entry, tuple):
            name, comment, unit = entry
            s += '%-8s  %-26s %s\n' % (name, comment, unit)
        else:
            # impossible
            raise TypeError, 'wrong construction of _help list'
    return s

# add the description of the units to the module's doc string:
__doc__ += '\n' + description()

if __name__ == '__main__':

#    from Scientific.N import *
    l = Quantity(10., 'm')
    big_l = Quantity(10., 'km')
    print big_l + l
    t = Quantity(314159., 's')
    print t.inUnitsOf('d','hr','min','s')

    p = Quantity # just a shorthand...

    e = p('2.7 Hartree*Nav')
    e.convertToUnit('kcal/mol')
    print e
    print e.inBaseUnits()

    freeze = p('0 degC')
    print freeze.inUnitsOf ('degF')

    euro = Quantity('1 EUR')
    print euro.inUnitsOf('DEM')

    if rc['fetchCurrencyRates']:
        print euro.inUnitsOf('USD')

    euroSQM = Quantity('19.99 EUR/m**2')
    print "%s=%s" % (euroSQM,euroSQM.inUnitsOf('EUR/cm**2'))

    bitrate = Quantity('1Kibit/s')
    print "%s=%s" % (bitrate,bitrate.inUnitsOf('kbit/s'))

    byterate = Quantity('1MiB/s')
    print "%s=%s" % (byterate,byterate.inUnitsOf('MB/s'))
    print "%s=%s" % (byterate,byterate.inUnitsOf('Mibit/s'))
