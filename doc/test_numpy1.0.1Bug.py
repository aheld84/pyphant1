import numpy
a = numpy.array([1,2,3])
b = numpy.array([0.1,0.2,0.3])
print numpy.rec.fromarrays([a,b],names='A,B')
print numpy.rec.fromarrays([a,b],names='A,B',titles='Spalte 1,Spalte 2')
