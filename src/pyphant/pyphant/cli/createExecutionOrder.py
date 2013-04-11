import pkg_resources
pkg_resources.require('pyphant')
pkg_resources.require('pyphant.imageprocessing')
pkg_resources.require('tables')
from pyphant.core import PyTablesPersister
from pyphant.core.H5FileHandler import H5FileHandler
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
    plugs = recipe.getAllPlugs()
    for p in plugs:
        parser.add_option("","--%s"%p.id,
                          help="Request result of plug %s"%p.id,
                          action="append_const", const=p, dest="requestedResults")
    (options, args) = parser.parse_args(filter(lambda o: 'plug' in o, argv))
    if hasattr(options, "requestedResults") and options.requestedResults and len(options.requestedResults)>0:
        openSockets = sum([recipe.getOpenSocketsForPlug(p) for p in options.requestedResults], [])
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
    parser.add_option("-n", "--max-orders-per-file", help="Maximal number of orders per file", type="int", dest="maxOrders")
    (options, args) = parser.parse_args(argv)
    # Order ::= (socketMap, resultPlug)
    return (options, args, recipe, [(options.socketMap, [p.id for p in options.requestedResults])])

from ImageProcessing.ImageLoaderWorker import ImageLoaderWorker
def f2dc(f):
    il = ImageLoaderWorker()
    il.paramFilename.value=f
    res = il.plugLoadImageAsGreyScale.getResult()
    res.seal()
    return res

import glob
from pyphant.core.KnowledgeManager import KnowledgeManager
km = KnowledgeManager.getInstance()
def globOrder(order, h5):
    sockMap = {}
    for sSpec in order[0].iteritems():
        if sSpec[1].startswith('emd5://'):
            sockMap[sSpec[0]] = [sSpec[1]]
        else:
            ids = []
            for f in glob.iglob(sSpec[1]):
                dc = f2dc(f)
                if h5 != None:
                    PyTablesPersister.saveResult(dc, h5)
                km.registerDataContainer(dc)
                ids.append(dc.id)
            sockMap[sSpec[0]] = ids
    return (sockMap, order[1])

def main():
    import tables, copy
    sourcefile = sys.argv[1]
    h5 = tables.openFile(sourcefile, 'r+')
    options, args, recipe, orders = processArgs(h5)
    h5.close()
    import os.path
    km.registerURL("file://"+os.path.realpath(sourcefile))
    orderLists = []
    for order in orders:
        order = globOrder(order, None)
        singles = dict([(socket, id[0]) for socket, id in order[0].iteritems() if len(id)==1])
        lists = dict([(socket, id) for socket, id in order[0].iteritems() if len(id)>1])
        lens = [len(l) for l in lists.itervalues()]
        assert max(lens) == min(lens), "Illegal lengths."
        count = lens[0]
        orderList = []
        for i in xrange(count):
            sockMap = copy.deepcopy(singles)
            for s, l in lists.iteritems():
                sockMap[s] = l[i]
            orderList.append((sockMap, order[1]))
        orderLists.append(orderList)
    orders = sum(orderLists,[])
    if options.maxOrders == None:
        count = len(orders)
    else:
        import math
        count = options.maxOrders
    i=0
    orderLists = []
    while i+count<len(orders):
        orderLists.append(orders[i:i+count])
        i+=count
    orderLists.append(orders[i:])
    for i, orderList in enumerate(orderLists):
        filename = os.path.basename(sourcefile)[:-3]+'_%i.h5'%i
        with H5FileHandler(filename, 'w') as handler:
            handler.saveRecipe(recipe)
        h5 = tables.openFile(filename, 'r+')
        for o in orderList:
            PyTablesPersister.saveExecutionOrder(h5, o)
            for data in o[0].values():
                dc = km.getDataContainer(data)
                PyTablesPersister.saveResult(dc, h5)
        h5.close()
    #PyTablesPersister.saveExecutionOrder(h5, o)


if __name__=='__main__':
    main()
