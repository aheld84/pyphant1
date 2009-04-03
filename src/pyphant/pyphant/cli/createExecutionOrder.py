import pkg_resources
pkg_resources.require('pyphant')
from pyphant.core import PyTablesPersister
import optparse
import sys

def processArgs(h5):
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv:
        help = True
    else:
        help = False
    args = filter(lambda a: not a in ['-h', '--help'], argv)
    parser = optparse.OptionParser()
    recipeFile = argv[0]
    recipe = PyTablesPersister.loadRecipe(h5)
    plugs = sum([w.getPlugs() for w in recipe.getWorkers()], [])
    for p in plugs:
        parser.add_option("","--%s"%p.id,
                          help="Request result of plug %s"%p.id,
                          action="append_const", const=p, dest="requestedResults")
    (options, args) = parser.parse_args(filter(lambda o: 'plug' in o, argv))
    if hasattr(options, "requestedResults") and options.requestedResults and len(options.requestedResults)>0:
        walker = recipe.createCompositeWorkerWalker()
        openSockets = sum([sum(walker.visit(lambda w: [s for s in w.getSockets() if not s.isFull()],
                                            [p.worker]), []) 
                           for p in options.requestedResults], [])
        parser.values.socketMap = {}
        def optCallback(opt, opt_str, value, parser, socket):
            try:
                parser.values.socketMap[socket.id] = value
            except:
                parser.values.socketMap = {}
                parser.values.socketMap[socket.id] = value
        for s in openSockets:
            parser.add_option("","--%s"%s.id,
                              help="Feed socket %s with data from argument."%s.id,
                              action="callback", callback=optCallback, nargs=1, type='string',
                              callback_args=(s,))
    if help:
        args.append('-h')
    (options, args) = parser.parse_args(argv)
    # Order ::= (socketMap, resultPlug)
    return [(options.socketMap, [p.id for p in options.requestedResults])]

from ImageProcessing.ImageLoaderWorker import ImageLoaderWorker
def f2dc(f):
    il = ImageLoaderWorker()
    il.paramFilename.value=f
    res = il.plugLoadImageAsGreyScale.getResult()
    res.seal()
    return res

import glob
def globOrder(h5, order):
    sockMap = {}
    for sSpec in order[0].iteritems():
        if sSpec[1].startswith('emd5://'):
            sockMap[sSpec[0]] = [sSpec[1]]
        else:
            ids = []
            for f in glob.iglob(sSpec[1]):
                dc = f2dc(f)
                PyTablesPersister.saveResult(dc, h5)
                ids.append(dc.id)
            sockMap[sSpec[0]] = ids
    return (sockMap, order[1])

def main():
    import tables, copy
    h5 = tables.openFile(sys.argv[1], 'r+')
    orders = processArgs(h5)
    for order in orders:
        order = globOrder(h5, order)
        singles = dict([(socket, id[0]) for socket, id in order[0].iteritems() if len(id)==1])
        lists = dict([(socket, id) for socket, id in order[0].iteritems() if len(id)>1])
        lens = [len(l) for l in lists.itervalues()]
        assert max(lens) == min(lens), "Illegal lengths."
        count = lens[0]
        for i in xrange(count):
            sockMap = copy.deepcopy(singles)
            for s, l in lists.iteritems():
                sockMap[s] = l[i]
            PyTablesPersister.saveExecutionOrder(h5, (sockMap, order[1]))
    h5.close()


if __name__=='__main__':
    main()
