import sys
from fmfile.FMFLoader import FMFLoader

worker = FMFLoader()
if len(sys.argv) == 1:
    filenames = ['example.fmf']
else:
    filenames = sys.argv[1:]
for filename in filenames:
    worker.paramFilename.value=filename
    result = worker.plugLoadFMF.getResult()
    print result
    print result.attributes
