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

import matplotlib
matplotlib.use('wxagg') # This MUST stay in front of 'import pylab'!
import threading, pylab
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
def processArgs():
    from optparse import OptionParser
    visualizationThemes = ("compareAbsorption",
                           "noisyAbsorption",
                           "thicknessMap",
                           "functional",
                           "simulation",
                           "dumpMinima")
    parser = OptionParser(usage="usage: %prog [options] path2recipe")
    parser.add_option("-n", "--number", dest="curvNo",type='long',
                      help="Number of curve set to visualize", metavar="CURVNO",default=1)
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
    recipe = pyphant.core.PyTablesPersister.loadRecipeFromHDF5File(args[0])
    return (args[0], options, recipe)

def curvNo2Index(pixel, curvNo):
    import numpy
    index = numpy.where(pixel.data==curvNo)
    if len(index)>1 or len(index[0])>1:
        raise RuntimeError, "Invalid curvNo %s: Found index: %s" %(curvNo,index)
    return index[0][0]

def setParameters(recipe, freqRange=None, scale=None):
    if freqRange != None:
        worker = recipe.getWorker("Slicing")
        worker.paramDim1.value=freqRange
    if scale != None:
        worker = recipe.getWorker("MRA Exp")
	worker.paramScale.value=scale

def initPylab(postscript):
    pylab.hold = True
    if postscript:
        inches_per_pt = 1.0/72.27
        golden_mean = (5.0**0.5+1)/2.0
        figwidth=246. * inches_per_pt
        figheight = (figwidth / golden_mean)
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

def finalizePylab(postscript, visualizer=None):
    if postscript:
        from os.path import basename
        filename = '%s-%s-n%s.eps' % (basename(pathToRecipe)[:-3],theme,curvNo)
        if visualizer != None:
            visualizer.figure.savefig(filename)
        else:
            pylab.savefig(filename)
    else:
        pylab.show()

def compareAbsorption(recipe, curvNo, noIndicators):
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Result Functional"))
    xPos = table[u"x-position"]
    yPos = table[u"y-position"]
    index = curvNo2Index(table[u"pixel"], curvNo)
    title_template = "$%%s_{%s}$(%s %s,%s %s)=%%s %%s" % (curvNo,
                                               xPos.data[index],xPos.unit.unit.name(),
                                               yPos.data[index],yPos.unit.unit.name())

    worker = recipe.getWorker("ThicknessModeller")
    simulation = worker.plugCalcAbsorption.getResult()

    thickness = table[u"thickness"]
    residuum = (simulation.dimensions[0].data-thickness.data[index])**2
    absorption = simulation.data[residuum.argmin(),:]
    pylab.plot(simulation.dimensions[1].data,
               absorption,label="$%s$ functional"%simulation.shortname)
    title = "Functional based: " + title_template % (thickness[index].shortname,
                                                     thickness.data[index],
                                                     thickness.unit.unit.name())

    try:
        worker = recipe.getWorker("Res Direct")
        table = worker.plugCompute.getResult(subscriber=TextSubscriber("Result without Functional"))
        thickness = table[u"thickness"]
        residuum = (simulation.dimensions[0].data-thickness.data[index])**2
        absorption = simulation.data[residuum.argmin(),:]
        pylab.plot(simulation.dimensions[1].data,
                   absorption,label="$%s$ immediate"%simulation.shortname)
        title += "\nImmediate: " +  title_template % (thickness[index].shortname,
                                                      thickness.data[index],
                                                      thickness.unit.unit.name())
    except:
        pass

    worker = recipe.getWorker("Slicing")
    noisyAbsorption = worker.plugExtract.getResult()
    worker = recipe.getWorker("MRA Exp")
    minimaPos = worker.plugMra.getResult()[r'\lambda_{min}'].inUnitsOf(simulation.dimensions[1])
    maximaPos = worker.plugMra.getResult()[r'\lambda_{max}'].inUnitsOf(simulation.dimensions[1])
    pylab.plot(noisyAbsorption.dimensions[1].inUnitsOf(simulation.dimensions[1]).data,
               noisyAbsorption.data[index,:],label="$%s$"%noisyAbsorption.shortname)
    if not noIndicators:
        pylab.vlines(minimaPos.data[:,index],0.1,1.0,
                     label ="$%s$"%minimaPos.shortname)
        pylab.vlines(minimaPos.data[:,index]+minimaPos.error[:,index],0.1,1.0,
                     label ="$\\Delta%s$"%minimaPos.shortname, linestyle='dashed')
        pylab.vlines(minimaPos.data[:,index]-minimaPos.error[:,index],0.1,1.0,
                     label ="$\\Delta%s$"%minimaPos.shortname, linestyle='dashed')
        pylab.vlines(maximaPos.data[:,index],0.1,1.0,
                     label ="$%s$"%maximaPos.shortname)
        pylab.vlines(maximaPos.data[:,index]+maximaPos.error[:,index],0.1,1.0,
                     label ="$\\Delta%s$"%maximaPos.shortname, linestyle='dashed')
        pylab.vlines(maximaPos.data[:,index]-maximaPos.error[:,index],0.1,1.0,
                     label ="$\\Delta%s$"%maximaPos.shortname, linestyle='dashed')
    pylab.title(title)
    pylab.xlabel(simulation.dimensions[1].label)
    pylab.legend(loc="lower left")

def noisyAbsorption(recipe, curvNo, noIndicators):
    worker = recipe.getWorker("Slicing")
    noisyAbsorption = worker.plugExtract.getResult()
    worker = recipe.getWorker("ThicknessModeller")[0]
    simulation = worker.plugCalcAbsorption.getResult()
    worker = recipe.getWorker("MRA Exp")
    minimaPos = worker.plugMra.getResult()[r'\lambda_{min}'].inUnitsOf(simulation.dimensions[1])
    maximaPos = worker.plugMra.getResult()[r'\lambda_{max}'].inUnitsOf(simulation.dimensions[1])
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))
    xPos = table[u"x-position"]
    yPos = table[u"y-position"]
    thickness = table[u"thickness"]
    index = curvNo2Index(table[u"pixel"], curvNo)
    result = "$%s_{%s}$(%s %s,%s %s)=%s %s" % (thickness[index].shortname,curvNo,
                                               xPos.data[index],xPos.unit.unit.name(),
                                               yPos.data[index],yPos.unit.unit.name(),
                                               thickness.data[index],
                                               thickness.unit.unit.name())
    pylab.plot(noisyAbsorption.dimensions[1].inUnitsOf(simulation.dimensions[1]).data,
               noisyAbsorption.data[index,:],label="$%s$"%noisyAbsorption.shortname)
    if not noIndicators:
        pylab.vlines(minimaPos.data[:,index],0.1,1.0,
                     label ="$%s$"%minimaPos.shortname)
        pylab.vlines(maximaPos.data[:,index],0.1,1.0,
                     label ="$%s$"%maximaPos.shortname)
    pylab.title(result)
    pylab.xlabel(simulation.dimensions[1].label)
    pylab.ylabel(simulation.label)

def thicknessMap(recipe, curvNo):
    worker = recipe.getWorker("OscMapper")
    oscMap = worker.plugMapHeights.getResult()
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))
    xPos = table[u"x-position"]
    yPos = table[u"y-position"]
    index = curvNo2Index(table[u"pixel"], curvNo)
    visualizer = ImageVisualizer(oscMap, False)
    pylab.plot([xPos.data[index]],[yPos.data[index]],'xk',scalex=False,scaley=False)

def functional(recipe, curvNo, noIndicators):
    worker = recipe.getWorker("Compute Functional")
    functional = worker.plugCompute.getResult()[r'F_{\lambda_{min}}']
    worker = recipe.getWorker("ThicknessModeller")
    simulation = worker.plugCalcAbsorption.getResult()
    worker = recipe.getWorker("MRA Exp")
    minimaPos = worker.plugMra.getResult()[r'\lambda_{min}'].inUnitsOf(simulation.dimensions[1])
    maximaPos = worker.plugMra.getResult()[r'\lambda_{max}'].inUnitsOf(simulation.dimensions[1])
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))
    thickness = table[u"thickness"]
    index = curvNo2Index(table[u"pixel"], curvNo)
    visualizer = ImageVisualizer(functional, False)
    if not noIndicators:
        ordinate = functional.dimensions[1].data
        pylab.hlines(minimaPos.data[:,index],ordinate.min(),ordinate.max(),
                     label ="$%s$"%minimaPos.shortname)
        pylab.hlines(maximaPos.data[:,index],ordinate.min(),ordinate.max(),
                     label ="$%s$"%maximaPos.shortname)
        abscissae = functional.dimensions[0].data
        pylab.vlines(thickness.data[index],abscissae.min(),abscissae.max(),
                     label ="$%s$"%minimaPos.shortname)

def simulation(recipe, curvNo, noIndicators):
    worker = recipe.getWorker("ThicknessModeller")
    simulation = worker.plugCalcAbsorption.getResult()
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))
    thickness = table[u"thickness"]
    index = curvNo2Index(table[u"pixel"], curvNo)
    worker = recipe.getWorker("MRA Exp")
    minimaPos = worker.plugMra.getResult()[r'\lambda_{min}'].inUnitsOf(simulation.dimensions[1])
    maximaPos = worker.plugMra.getResult()[r'\lambda_{max}'].inUnitsOf(simulation.dimensions[1])
    visualizer = ImageVisualizer(simulation, False)
    ordinate = simulation.dimensions[1].data
    if not noIndicators:
        pylab.hlines(thickness.data[index],ordinate.min(),ordinate.max(),
                     label ="$%s$"%minimaPos.shortname)
        abscissae = simulation.dimensions[0].data
        pylab.vlines(minimaPos.data[:,index],abscissae.min(),abscissae.max(),
                     label ="$%s$"%minimaPos.shortname)
        pylab.vlines(maximaPos.data[:,index],abscissae.min(),abscissae.max(),
                     label ="$%s$"%maximaPos.shortname)

def dumpMinima(recipe):
    worker = recipe.getWorker("ThicknessModeller")
    simulation = worker.plugCalcAbsorption.getResult()
    worker = recipe.getWorker("AddColumn")
    table = worker.plugCompute.getResult(subscriber=TextSubscriber("Add Column"))
    index = table[u"pixel"]
    xPos = table[u"x-position"]
    yPos = table[u"y-position"]
    thickness = table[u"thickness"]
    cols = [index, xPos, yPos, thickness]
    worker = recipe.getWorker("MRA Exp")
    minimaPos = worker.plugMra.getResult()[r'\lambda_{min}'].inUnitsOf(simulation.dimensions[1])
    import numpy
    data = numpy.vstack([ c.data for c in cols]
                        + numpy.vsplit(minimaPos.data, len(minimaPos.data))).transpose()
    import fmfile.fmfgen
    factory = fmfile.fmfgen.gen_factory(out_coding='cp1252', eol='\r\n')
    fc = factory.gen_fmf()
    fc.add_reference_item('author', "Kristian")
    tab = factory.gen_table(data)
    for c in cols:
        tab.add_column_def(c.longname, c.shortname, str(c.unit))
    for i in xrange(len(minimaPos.data)):
        tab.add_column_def("minimaPos%i"%i, "p_%i"%i)
    fc.add_table(tab)
    print str(fc)

def main():
    pathToRecipe, options, recipe = processArgs()
    setParameters(recipe, options.freqRange, options.scale)
    initPylab(options.postscript)
    if options.theme == "compareAbsorption":
        compareAbsorption(recipe, options.curvNo, options.noIndicators)
    elif options.theme == "noisyAbsorption":
        noisyAbsorption(recipe, options.curvNo, options.noIndicators)
    elif options.theme == "thicknessMap":
        thicknessMap(recipe, options.curvNo)
    elif options.theme == "functional":
        functional(recipe, options.curvNo, options.noIndicators)
    elif options.theme == "simulation":
        simulation(recipe, options.curvNo, options.noIndicators)
    elif options.theme == "dumpMinima":
        dumpMinima(recipe)
    finalizePylab(options.postscript)
    pyphant.core.PyTablesPersister.saveRecipeToHDF5File(recipe, pathToRecipe)

if __name__ == '__main__':
    main()
