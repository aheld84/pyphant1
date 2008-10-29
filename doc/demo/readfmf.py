from fmfile.FMFLoader2 import FMFLoader2

worker = FMFLoader2()
worker.paramFilename.value='example.fmf'
result = worker.plugLoadFMF.getResult()
print result
print result.attributes
