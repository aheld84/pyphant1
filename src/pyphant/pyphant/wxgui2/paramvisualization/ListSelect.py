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

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

import wx
from wx import EVT_CHOICE
from pyphant.core.Param import (
    ParamChangeExpected, PossibleValuesChangeExpected)

class ListSelect(wx.Choice):
    def __init__(self, parent, param, validator):
        self.data = dict([(str(v), v) for v in param.possibleValues])
        wx.Choice.__init__(self, parent,
                           choices=map(str, param.possibleValues),
                           validator=validator)
        self.SetValue(param.value)

    def getValue(self):
        if self.GetSelection()==wx.NOT_FOUND:
            raise ValueError("Invalid value")
        else:
            return self.data[self.GetStringSelection()]

    def SetValue(self, value):
        self.SetStringSelection(str(value))


class InstantSelect(ListSelect):
    """
    This class dispatches the ParamChangeExpected event as soon as
    the user selects a new value and listens for the
    PossibleValueChangeExpected event which should be raised
    if the possible values for the underlying ListSelect
    need to be updated.
    """
    def __init__(self, parent, param, validator):
        ListSelect.__init__(self, parent, param, validator)
        self.Bind(EVT_CHOICE, self.onChoice)
        self.param = param
        self.possibleValues = param.possibleValues
        param._eventDispatcher.registerExclusiveListener(
            self.onPVCE, PossibleValuesChangeExpected)

    def onPVCE(self, event):
        value = self.data[self.GetStringSelection()]
        assert value in event.expectedPVs, "%s not in %s" % (value,
                                                             event.expectedPVs)
        self.data = dict([(str(val), val) for val in event.expectedPVs])
        self.possibleValues = event.expectedPVs
        self.SetItems(map(str, event.expectedPVs))
        if event.autoSelect and len(event.expectedPVs) == 2:
            self.SetSelection(1)
            pce = ParamChangeExpected(
                self.param, expectedValue=self.data[self.GetStringSelection()])
            pce.norefresh = True
            self.param._eventDispatcher.dispatchEvent(pce)
        else:
            self.SetValue(value)

    def onChoice(self, event):
        event.Skip()
        self.param._eventDispatcher.dispatchEvent(
            ParamChangeExpected(
            self.param, expectedValue=self.data[self.GetStringSelection()]))

    def getValue(self):
        if self.GetSelection()==wx.NOT_FOUND:
            raise ValueError("Invalid value")
        else:
            self.param.possibleValues = self.possibleValues
            return self.data[self.GetStringSelection()]
