# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
# Copyright (c) 2009,  Andreas W. Liehr (liehr@users.sourceforge.net)
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

u"""Provides unittest classes TestMRA and TestMRADiscontinuousDiscretisation.
"""



import unittest


import numpy
from pyphant.core import DataContainer as DC


class TestEmd5Source(unittest.TestCase):
    """Sets up a random FieldContainer and ragisters it with the
    knowledge manager."""
    def setUp(self):
        self.V = DC.FieldContainer(numpy.random.randn(10,10))
        self.V.seal()
        from pyphant.core import KnowledgeManager
        KnowledgeManager.KnowledgeManager.getInstance(
            ).registerDataContainer(self.V, temporary=True)

    def testEmd5Source(self):
        """Retrieves the previously registered FieldContainer via the
        Emd5Source and checks for equality."""
        #Predict result
        from pyphant.core.Emd5Src import Emd5Src
        s = Emd5Src()
        s.paramEmd5.value = self.V.id
        result = s.plugGetDataContainer.getResult()
        self.assertEqual(result, self.V)

if __name__ == '__main__':
    unittest.main()
