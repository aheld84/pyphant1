#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
import os, os.path

import sys

import unittest

suites = []
for root, dirs, files in os.walk("."):
    for i, d in enumerate(dirs):
        if d == ".svn":
            del dirs[i]

    files = filter(lambda f: f.startswith('Test') and f.endswith('.py'), files)

    if len(files)>0:
        sys.path.append(root)
        for f in files:
            mod = f[:-3]
            exec 'import '+mod
            mod = sys.modules[mod]
            suites.append(unittest.TestLoader().loadTestsFromModule(mod))


suite = unittest.TestSuite(suites)

unittest.TextTestRunner().run(suite)
