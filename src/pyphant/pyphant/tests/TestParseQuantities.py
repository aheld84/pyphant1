#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2009, Rectorate of the University of Freiburg
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

# $Source$

import pkg_resources
pkg_resources.require('pyphant')

import unittest, numpy
from pyphant.quantities.ParseQuantities import parseDateTime
from pyphant.quantities import Quantity
"""
    >>>parseDateTime('2004-08-21 12:00:00+-12hr')
    (Quantity(731814.5,'d'), Quantity(0.5,'d'))
    >>>parseDateTime('2004-08-21 12:00:00')
    (Quantity(731814.5,'d'), None)
"""
class TestParseDateTime(unittest.TestCase):
    def testWithError(self):
        self.assertEqual(parseDateTime('2004-08-21 12:00:00+-12hr'),
                         (Quantity(731814.5,'d'), Quantity(0.5,'d'))
                         )

    def testWithErrorOldDeprecatedAbbreviation(self):
        self.assertEqual(parseDateTime('2004-08-21 12:00:00+-12h'),
                         (Quantity(731814.5,'d'), Quantity(0.5,'d'))
                         )

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
