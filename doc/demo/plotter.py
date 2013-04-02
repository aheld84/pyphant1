#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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

__id__ = "$Id$"
__author__ = "$Author: liehr $"

import pyphant.core.PyTablesPersister
from pyphant.visualizers.ImageVisualizer import F
from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options] path2recipe")
(options, args) = parser.parse_args()

if len(args) != 1:
        parser.error("incorrect number of arguments")
else:
    pathToRecipe = args[0]
#Load recipe from hdf file
recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(pathToRecipe)

#Get EstimatedWidth
worker = recipe.getWorkers("Add Column")[0]
table = worker.plugCompute.getResult()

xPos = table[u"horizontal_table_position"]
yPos = table[u"vertical_table_position"]
thickness = table[u"thickness"]

import matplotlib
from matplotlib.pyplot import figure, show, subplot, colorbar
from matplotlib.patches import Circle
from numpy import ones

fig = figure()
ax = subplot(111) #fig.add_axes([xPos.data.min(), yPos.data.min(), xPos.data.max(), yPos.data.max()])
ax.set_xlim(xPos.data.min()-0.4, xPos.data.max()+0.4)
ax.set_ylim(yPos.data.min()-0.4, yPos.data.max()+0.4)
ax.set_xlabel(xPos.label)
ax.set_ylabel(yPos.label)
sm = matplotlib.cm.ScalarMappable(cmap=matplotlib.cm.jet)
sm.set_array(thickness.data)
sm.autoscale()
sm.get_alpha = lambda : 1
for x, y, z  in zip(xPos.data, yPos.data, thickness.data):
    ax.add_patch(Circle((x,y), 0.4, facecolor=sm.to_rgba(z), lw=0))
fig.colorbar(sm, ax=ax,format=F(thickness))
show()

