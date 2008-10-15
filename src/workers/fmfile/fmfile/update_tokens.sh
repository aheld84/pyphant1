#!/bin/bash
java -cp /Users/zklaus/src/antlr-3.0.1/lib/antlr-2.7.7.jar:/Users/zklaus/src/antlr-3.0.1/lib/stringtemplate-3.1b1.jar:/Users/zklaus/src/antlr-3.0.1/lib/antlr-3.0.1.jar org.antlr.Tool FMFpython.g FMFpythonTree.g
echo tokens = { >tokens.py && sed 's/\([^=]*\)=\(.*\)/    \2 : "\1",/g' FMFpython.tokens >>tokens.py && echo } >>tokens.py

