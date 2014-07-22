#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2014, Rectorate of the University of Freiburg
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


"""
Pyphant Organic Solar Cells toolbox
Visit http://pyphant.sourceforge.net for more information.
"""


VERSION = '1.0b4.dev'

from setuptools import setup, find_packages
from setuptools.command.test import test


class EnsureAggUnittests(test):
    def run_tests(self):
        from pyphant.mplbackend import ensure_mpl_backend
        ensure_mpl_backend('agg')
        return test.run_tests(self)


setup(
    name="pyphant.osc",
    version=VERSION,
    author="Andreas W. Liehr, Klaus Zimmermann",
    author_email='klaus.zimmermann@fmf.uni-freiburg.de',
    maintainer='SGWissInfo',
    maintainer_email='servicegruppe.wissinfo@fmf.uni-freiburg.de',
    license="BSD",
    description=__doc__,
    install_requires=[
        'pyphant>=1.0b4.dev',
        'numpy',
        'scipy',
        'matplotlib',
        ],
    packages=find_packages(),
    entry_points="""
    [pyphant.workers]
    myeentry = OSC
    """,
    include_package_data=True,
    cmdclass={'test': EnsureAggUnittests},
    test_suite='OSC.tests'
    )
