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

import OneLineStringField
import BoundedIntegerTextField
import CheckBox
import ListSelect
import FileButton
from pyphant.core import Connectors, Param
import wx


class NullVal(wx.PyValidator):
    def Clone(self):
        return NullVal()

    def Validate(self, win):
        return True


class ParamValidator(wx.PyValidator):
    def __init__(self, param):
        wx.PyValidator.__init__(self)
        self.param = param

    def Clone(self):
        return ParamValidator(self.param)

    def Validate(self, win):
        ctrl = self.GetWindow()
        newValue = ctrl.getValue()
        try:
            self.param.value = newValue
        except Param.VetoParamChange, e:
            wx.MessageBox("%s" % str(e),
                          "Invalid Parameter %s" % self.param.name)
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        return True

    def TransferToWindow(self):
        ctrl = self.GetWindow()
        ctrl.SetValue(self.param.value)
        True

    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        self.param.value = ctrl.getValue()
        True


class ParamVisReg:
    def __init__(self):
        self._visualizers={}
        register = [
            (0, None, BoundedIntegerTextField.BoundedIntegerTextField),
            (" ", None, OneLineStringField.OLSF),
            (" ", Connectors.SUBTYPE_FILE, FileButton.FileButton),
            (True, None, CheckBox.CheckBox),
            (True, Connectors.SUBTYPE_INSTANT, CheckBox.InstantCheckBox),
            ([], None, ListSelect.ListSelect),
            ([], Connectors.SUBTYPE_INSTANT, ListSelect.InstantSelect)
            ]
        for prototype, subtype, visualizer in register:
            self.setVisualizer(type(prototype), subtype, visualizer)

    def setVisualizer(self, type, subtype, visualizer):
        try:
            typedict=self._visualizers[type]
        except KeyError:
            typedict={}
            self._visualizers[type]=typedict
        typedict[subtype]=visualizer

    def createVisualizerFor(self, parent, param, validator=None):
        if validator==None:
            validator=ParamValidator(param)
        return self._visualizers[param.valueType][param.subtype](
            parent, param, validator=validator)
