# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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

import Connectors, EventDispatcher

def createParam(worker, paramName, displayName, values, subtype=None):
    if isinstance(values, list):
        return SelectionParam(worker, paramName, displayName,
                              values, subtype)
    else:
        return Param(worker, paramName, displayName, values, subtype)


class ParamChangeExpected(object):
    def __init__(self, param, expectedValue):
        self.param = param
        self.expectedValue = expectedValue


class PossibleValuesChangeExpected(object):
    def __init__(self, param, expectedPVs, autoSelect=False):
        self.param = param
        self.expectedPVs = expectedPVs
        self.autoSelect = autoSelect


class ParamChangeRequested(object):
    def __init__(self, param, oldValue, newValue):
        self.param = param
        self.oldValue = oldValue
        self.newValue = newValue


class ParamChanged(object):
    def __init__(self, param, oldValue, newValue):
        self.param = param
        self.oldValue = oldValue
        self.newValue = newValue


class ParamOverridden(object):
    def __init__(self, param, oldValue, newValue):
        self.param = param
        self.oldValue = oldValue
        self.newValue = newValue


class VetoParamChange(ValueError):
    def __init__(self, paramChangeEvent):
        ValueError.__init__(self, "Veto: change %s from %s to %s." %
                            (paramChangeEvent.param.name,
                             paramChangeEvent.oldValue,
                             paramChangeEvent.newValue))
        self.paramChangeEvent = paramChangeEvent


class Param(Connectors.Socket):
    def __getValue(self):
        if self.isFull():
            return self.getResult()
        else:
            return self._value

    def overrideValue(self, value):
        oldValue = self._value
        self._value = value
        self._eventDispatcher.dispatchEvent(
            ParamOverridden(self, oldValue, value))

    def __setValue(self, value):
        oldValue = self.value
        if oldValue == value:
            return
        self._eventDispatcher.dispatchEvent(
            ParamChangeRequested(self, oldValue, value)
            )
        self._value = value
        self._eventDispatcher.dispatchEvent(
            ParamChanged(self, oldValue, value)
            )
        self.invalidate()

    value = property(__getValue, __setValue)

    def __init__(self, worker, name, displayName, value, subtype=None):
        Connectors.Socket.__init__(self, worker, name, type(value))
        self.isExternal = False
        self.valueType = type(value)
        self.displayName = displayName
        self._value = value
        self.subtype = subtype
        self._eventDispatcher = EventDispatcher.EventDispatcher()

    def registerListener(self, vetoer, eventType):
        self._eventDispatcher.registerListener(vetoer, eventType)

    def unregisterListener(self, vetoer, eventType):
        self._eventDispatcher.unregisterListener(vetoer, eventType)

    #pickle
    def __getstate__(self):
        import copy
        pdict = copy.copy(self.__dict__)
        pdict['_eventDispatcher'] = EventDispatcher.EventDispatcher()
        return pdict


class SelectionParam(Param):
    def __init__(self, worker, name, displayName, values, subtype=None):
        Param.__init__(self, worker, name, displayName, values[0], subtype)
        self.valueType = type(values)
        self._possibleValues = values

    def getPossibleValues(self):
        return self._possibleValues

    def __getPossibleValues(self):
        return self.getPossibleValues()

    def setPossibleValues(self, values):
        self._possibleValues = values

    def __setPossibleValues(self, values):
        oldValues = self.possibleValues
        if oldValues == values:
            return
        self.setPossibleValues(values)
        self.invalidate()

    possibleValues = property(__getPossibleValues, __setPossibleValues)
