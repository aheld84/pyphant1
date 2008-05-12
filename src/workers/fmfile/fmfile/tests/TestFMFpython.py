# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import antlr3
import antlr3.tree
from FMFpythonLexer import FMFpythonLexer 
from FMFpythonParser import FMFpythonParser
from FMFpythonTree import FMFpythonTree

char_stream = antlr3.ANTLRFileStream("Sim_abs_210nm.dat", "utf-8")
lexer = FMFpythonLexer(char_stream)
#t = lexer.nextToken()
#while t.getText():
#    print t.getText()
#    t = lexer.nextToken()
tokens = antlr3.CommonTokenStream(lexer)
parser = FMFpythonParser(tokens)
r = parser.config()
#print r.tree.children

nodes = antlr3.tree.CommonTreeNodeStream(r.tree)
nodes.setTokenStream(tokens)
walker = FMFpythonTree(nodes)
data = walker.dataContainer()

import pkg_resources
pkg_resources.require('Pyphant')
import pyphant.visualizers.Chart as cv

v = cv.LineChart(data['absorption'])
v.figure.savefig('toll.png')


