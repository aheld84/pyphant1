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
__version__ = "$Revision: 29 $"

import threading
from pyphant.visualizers.ImageVisualizer import ImageVisualizer

class TextSubscriber(object):
    def __init__(self, plugName):
        title = u"Calculating %s" % plugName
        message = u"Calculating the result of %s" % plugName
        self.processes={}
        self.count=0
        self.cv=threading.Condition()
        self.percentage=0
        self.share=1.0

    def update(self):
        self.cv.acquire()
        self.cv.wait(0.1)
        print self.percentage, "%%"
        self.cv.release()

    def startProcess(self, process):
        self.processes[process]=0
        self.share=1.0/len(self.processes)
        self.updatePercentage()

    def updatePercentage(self):
        self.cv.acquire()
        self.percentage=int(sum([x*self.share for x in self.processes.values()]))
        print self.percentage, "%%"
        self.count+=1
        self.cv.notify()
        self.cv.release()

    def updateProcess(self, process, value):
        self.processes[process]=value
        self.updatePercentage()

    def finishProcess(self, process):
        self.processes[process]=100
        self.updatePercentage()

    def finishAllProcesses(self):
        self.cv.acquire()
        self.percentage=100
        self.updatePercentage()
        self.cv.release()


import pyphant.core.PyTablesPersister
visualizer = None 
from optparse import OptionParser

visualizationThemes = ("compareAbsorption",
                       "noisyAbsorption",
                       "thicknessMap",
                       "functional",
                       "simulation")

parser = OptionParser(usage="usage: %prog [options] path2recipe")

parser.add_option("-n", "--number", dest="curvNo",type='long',
                  help="Number of curve set to visualize", metavar="CURVNO",default=0)
parser.add_option("-f", "--frequency-range", dest="freqRange", type="str",
		  help="Frequency range to use for data slicing.", metavar="FREQRANGE", default=None)
parser.add_option("-s", "--scale", dest="scale", type="str",
		  help="Scale parameter", metavar="SCALE", default=None)

parser.add_option("-v", "--visualize", dest="theme", type="choice",choices = visualizationThemes,
                  help="Choose visualization theme from %s" % str(visualizationThemes),
                  metavar="THEME", default=visualizationThemes[0])
parser.add_option("-p", "--postscript", dest="postscript", action="store_true",
                  help="Write diagram to encapsulated postscript file.")
parser.add_option("-I", "--noIndicators", dest="noIndicators", action="store_true",
                  help="Don't show indicators like position, local minima, or estimated thickness.")

(options, args) = parser.parse_args()

if len(args) != 1:
        parser.error("incorrect number of arguments")
else:
    pathToRecipe = args[0]
    curvNo = options.curvNo
    freqRange = options.freqRange
    scale = options.scale
    theme = options.theme
    noIndicators = options.noIndicators
#Load recipe from hdf file
recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(pathToRecipe)

#Get Absorption
worker = recipe.getWorkers("Slicing")[0]
if freqRange != None:
    print freqRange, worker.paramDim1.value
    worker.paramDim1.value=freqRange
    noisyAbsorption = worker.plugExtract.getResult()

#Get Simulation
worker = recipe.getWorkers("Coat Thickness Model")[0]
simulation = worker.plugCalcAbsorption.getResult()

if scale != None:
	worker = recipe.getWorkers("Multi Resolution Analyser")[0]
	worker.paramScale.value=scale

if theme == visualizationThemes[2]:
    worker = recipe.getWorkers("Osc Mapper")[0]
    oscMap = worker.plugMapHeights.getResult()

if theme == visualizationThemes[3]:
    worker = recipe.getWorkers("Compute Functional")[0]
    functional = worker.plugCompute.getResult()

if theme == visualizationThemes[4]:
    worker = recipe.getWorkers("Coat Thickness Model")[0]
    simulation = worker.plugCalcAbsorption.getResult()

#Get EstimatedWidth
worker = recipe.getWorkers("Add Column")[0]
table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))

xPos = table[u"horizontal_table_position"]
yPos = table[u"vertical_table_position"]
thickness = table[u"thickness"]
filename = table[u"filename"]

result = "$%s_{%s}$(%s %s,%s %s)=%s %s" % (thickness[curvNo].shortname,curvNo,
                                 xPos.data[curvNo],xPos.unit.unit.name(),
                                 yPos.data[curvNo],yPos.unit.unit.name(),
                                 thickness.data[curvNo],
                                 thickness.unit.unit.name())
print "Visualizing file %s with %s." % (filename[curvNo].data[0],result)

#Compute reference simulation
residuum = (simulation.dimensions[0].data-thickness.data[curvNo])**2
absorption = simulation.data[residuum.argmin(),:]

#Get result of MRA
worker = recipe.getWorkers("Multi Resolution Analyser")[0]
minimaPos = worker.plugMra.getResult().inUnitsOf(simulation.dimensions[1])

pyphant.core.PyTablesPersister.saveRecipeToHDF5File(recipe, pathToRecipe)

#Visualize Result
import pylab
pylab.hold = True
inches_per_pt = 1.0/72.27
golden_mean = (5.0**0.5+1)/2.0
figwidth=246. * inches_per_pt
figheight = (figwidth / golden_mean)

if options.postscript:
    left = 0.2
    bottom = 0.25
    right = 0.95
    top = 0.90
    params = {'font.size':10,
              'axes.labelsize':10,
              'axes.titlesize':10,
              'text.fontsize':10,
              'xtick.labelsize':10,
              'ytick.labelsize':10,
              'text.usetex':True,
              'backend':'ps',
              'figure.figsize': [figwidth/(right-left),figheight/(top-bottom)]
              }
    pylab.rcParams.update(params)
    pylab.figure(1)
    pylab.clf()
    pylab.axes([left,bottom,right-left,top-bottom])
    
if theme == visualizationThemes[0]:
    pylab.plot(noisyAbsorption.dimensions[1].inUnitsOf(simulation.dimensions[1]).data,
               noisyAbsorption.data[curvNo,:],label="$%s$"%noisyAbsorption.shortname)
    pylab.plot(simulation.dimensions[1].data,
               absorption,label="$%s$"%simulation.shortname)
    if not noIndicators:
        pylab.vlines(minimaPos.data[:,curvNo],0.1,1.0,
                     label ="$%s$"%minimaPos.shortname)
    pylab.title(result)
    pylab.xlabel(simulation.dimensions[1].label)

elif theme == visualizationThemes[1]:
    pylab.plot(noisyAbsorption.dimensions[1].inUnitsOf(simulation.dimensions[1]).data,
               noisyAbsorption.data[curvNo,:],label="$%s$"%noisyAbsorption.shortname)
    if not noIndicators:
        pylab.vlines(minimaPos.data[:,curvNo],0.1,1.0,
                     label ="$%s$"%minimaPos.shortname)
    pylab.title(result)
    pylab.xlabel(simulation.dimensions[1].label)
    pylab.ylabel(simulation.label)

elif theme == visualizationThemes[2]:
    visualizer = ImageVisualizer(oscMap)
    pylab.plot([xPos.data[curvNo]],[yPos.data[curvNo]],'xk',scalex=False,scaley=False)

elif theme == visualizationThemes[3]:
    visualizer = ImageVisualizer(functional)
    if not noIndicators:
        ordinate = functional.dimensions[1].data
        pylab.hlines(minimaPos.data[:,curvNo],ordinate.min(),ordinate.max(),
                     label ="$%s$"%minimaPos.shortname)
        abscissae = functional.dimensions[0].data
        pylab.vlines(thickness.data[curvNo],abscissae.min(),abscissae.max(),
                     label ="$%s$"%minimaPos.shortname)
    
elif theme == visualizationThemes[4]:
    visualizer = ImageVisualizer(simulation)
    ordinate = simulation.dimensions[1].data
    if not noIndicators:
        pylab.hlines(thickness.data[curvNo],ordinate.min(),ordinate.max(),
                     label ="$%s$"%minimaPos.shortname)
        abscissae = simulation.dimensions[0].data
        pylab.vlines(minimaPos.data[:,curvNo],abscissae.min(),abscissae.max(),
                     label ="$%s$"%minimaPos.shortname)
        
if options.postscript:
    from os.path import basename
    filename = '%s-%s-n%s.eps' % (basename(pathToRecipe)[:-3],theme,curvNo)
    if visualizer:
        visualizer.figure.savefig(filename)
    else:
        pylab.savefig(filename)
else:
    pylab.show()

