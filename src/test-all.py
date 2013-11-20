#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyphant.mplbackend import ensure_mpl_backend
ensure_mpl_backend('agg')
import os
import os.path
import sys
import unittest

suites = []
for root, dirs, files in os.walk("."):
    for ignore in ('.git', 'dist', 'build', '__pycache__'):
        if ignore in dirs:
            dirs.remove(ignore)

    files = filter(lambda f: f.startswith('Test') and f.endswith('.py'), files)

    if len(files) > 0:
        sys.path.append(root)
        for f in files:
            mod = f[:-3]
            exec 'import ' + mod
            mod = sys.modules[mod]
            suites.append(unittest.TestLoader().loadTestsFromModule(mod))


suite = unittest.TestSuite(suites)

unittest.TextTestRunner().run(suite)
