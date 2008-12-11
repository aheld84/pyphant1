import sys
import logging
logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s:%(name)s:%(thread)d:%(module)s.%(funcName)s(l %(lineno)d):%(message)s")

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
