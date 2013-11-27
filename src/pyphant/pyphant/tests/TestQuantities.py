# -*- coding: utf-8 -*-

# Copyright (c) 2009, Rectorate of the University of Freiburg
# Copyright (c) 2009-2010, Andreas W. Liehr (liehr@users.sourceforge.net)
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



import unittest, numpy
from pyphant.quantities import Quantity
"""
    >>>Quantity('1V')
    Quantity(1.0,'d'), Quantity(0.5,'d'))
    >>>parseDateTime('2004-08-21 12:00:00')
    (Quantity(731814.5,'d'), None)
"""
class TestQuantity(unittest.TestCase):
    def setUp(self):
        self.quants = []
        self.quants.append(Quantity("1000 m"))
        self.quants.append(Quantity("1 km"))
        self.quants.append(Quantity("1000.1 m"))
        self.quants.append(0)
        self.quants.append(None)
        self.quants.append(Quantity("1000 s"))

    def testTextualQuantitySpecification(self):
        self.assertEqual(Quantity('1V'),
                         Quantity(1.0,'V')
                         )

    def testUnicodeQuantitySpecification(self):
        self.assertEqual(Quantity(u'1V'),
                         Quantity(1.0,'V')
                         )
        self.assertEqual(Quantity('1V'.encode('utf-8')),
                         Quantity(1.0,'V')
                         )

    def compare(self, quant0, cop, quant1, result):
        if cop == '==':
            expression = quant0 == quant1
        elif cop == '!=':
            expression = quant0 != quant1
        elif cop == '<=':
            expression = quant0 <= quant1
        elif cop == '>=':
            expression = quant0 >= quant1
        elif cop == '<':
            expression = quant0 < quant1
        elif cop == '>':
            expression = quant0 > quant1
        if expression != result:
            print "%s %s %s = %s, should be %s" % (quant0, cop, quant1,
                                                   expression, result)
        self.assertEqual(expression, result)

    def matrixTest(self, matrix, cop):
        for index0, quant0 in enumerate(self.quants):
            for index1, quant1 in enumerate(self.quants):
                self.compare(quant0, cop, quant1, matrix[index0][index1])

    def testComparisonOperationEqual(self):
        matrix = [[1, 1, 0, 0, 0, 0],
                  [1, 1, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0],
                  [0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 1]]
        self.matrixTest(matrix, '==')

    def testComparisonOperationNotEqual(self):
        matrix = [[0, 0, 1, 1, 1, 1],
                  [0, 0, 1, 1, 1, 1],
                  [1, 1, 0, 1, 1, 1],
                  [1, 1, 1, 0, 1, 1],
                  [1, 1, 1, 1, 0, 1],
                  [1, 1, 1, 1, 1, 0]]
        self.matrixTest(matrix, '!=')

    def testComparisonOperationLessOrEqual(self):
        matrix = [[1, 1, 1, 0, 0, 0],
                  [1, 1, 1, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0],
                  [0, 0, 0, 1, 0, 0],
                  [1, 1, 1, 1, 1, 1],
                  [0, 0, 0, 0, 0, 1]]
        self.matrixTest(matrix, '<=')

    def testComparisonOperationGreaterOrEqual(self):
        matrix = [[1, 1, 0, 0, 1, 0],
                  [1, 1, 0, 0, 1, 0],
                  [1, 1, 1, 0, 1, 0],
                  [0, 0, 0, 1, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 1]]
        self.matrixTest(matrix, '>=')

    def testComparisonOperationLess(self):
        matrix = [[0, 0, 1, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 1, 0, 1],
                  [0, 0, 0, 0, 0, 0]]
        self.matrixTest(matrix, '<')

    def testComparisonOperationGreater(self):
        matrix = [[0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [1, 1, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 1, 0]]
        self.matrixTest(matrix, '>')

    def testList(self):
        self.assertEqual(self.quants[1] in self.quants, True)
        self.assertEqual(self.quants[0] in self.quants[1:], True)
        self.assertEqual(self.quants[2] in self.quants[3:], False)
        self.assertEqual(self.quants[1] in [], False)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
