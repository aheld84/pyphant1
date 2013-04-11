# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008, Rectorate of the University of Freiburg
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

def getPyphantPath(subdir = ''):
    """
    returns full pyphant path with optional subdirectory
    subdir -- subdirectory that is created if it does not exist already,
              recursive creation of directories is supported also.
    """
    import os
    homedir = os.path.expanduser('~')
    if homedir == '~':
        homedir = os.getcwdu()
    path = os.path.join(homedir, '.pyphant', subdir)
    # Create the dir in a multi process save way:
    try:
        os.makedirs(path) #<-- ignores EEXIST in all but top recursion levels
    except OSError, ose:
        if ose.errno != os.errno.EEXIST:
            raise
    return path

def getUsername():
    import getpass
    return getpass.getuser()

def getMachine():
    import socket
    return unicode(socket.getfqdn(), 'utf-8')

def enableLogging():
    """
    Enables logging to stdout for debug purposes.
    """
    import logging
    import sys
    l = logging.getLogger("pyphant")
    l.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s [%(name)s|%(levelname)s] %(message)s')
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(f)
    l.addHandler(h)
    l.info("Logger 'pyphant' has been configured for debug purposes.")

def uc2utf8(stype):
    """
    Returns utf-8 encoded version of stype, if stype was unicode, else
    stype is returned.
    If stype is of ListType, the above applies for all entries of the list.
    """
    from types import UnicodeType, ListType
    def convert(arg):
        if isinstance(arg, UnicodeType):
            return arg.encode('utf-8')
        return arg
    if isinstance(stype, ListType):
        return map(convert, stype)
    return convert(stype)

def utf82uc(stype):
    """
    Returns a unicode object created from a utf-8 encoded string.
    If the input was unicode, it is returned unchanged.
    List are treated similar to uc2utf8, see docstring there.
    """
    from types import StringType, ListType
    def convert(arg):
        if isinstance(arg, StringType):
            return unicode(arg, 'utf')
        return arg
    if isinstance(stype, ListType):
        return map(convert, stype)
    return convert(stype)

def emd52dict(emd5):
    """
    returns a dictionary with keys
    ('machine', 'creator', 'date', 'hash', 'type')
    """
    emd5 = utf82uc(emd5)
    emd5_split = emd5.split('/')
    retdict = {}
    retdict['machine'] = emd5_split[2]
    retdict['creator'] = emd5_split[3]
    retdict['date'] = emd5_split[4]
    retdict['hash'] = emd5_split[5].split('.')[0]
    retdict['type'] = emd5_split[5].split('.')[1]
    return retdict

def batch(recipe, input, plug, longname, dobatch=True, temporary=False):
    """
    Runs the same recipe multiple times for different input data.
    The return value is either a SampleContainer similar to input
    with 'emd5' column replaced by results or the resulting
    DataContainer from plug, if dobatch is set to False.
    recipe -- CompositeWorker instance
    input -- SampleContainer with 'emd5' column or any DataContainer if
             dobatch is set to False
    plug -- plug contained in recipe to get output from
            (there has to be exactly one open socket in recipe
            ascending from plug)
    longname -- longname of resulting SampleContainer, works only for
                dobatch == True
    dobatch -- if set to False, input is treated as a single data source
    temporary -- whether to register results temporarily, only applies when
                 dobatch is set to True
    """
    socket = recipe.getOpenSocketsForPlug(plug)[0]
    from pyphant.core.Emd5Src import Emd5Src
    DummyWorker = Emd5Src()
    socket.insert(DummyWorker.getPlugs()[0])
    DummyWorker.paramSelectby.value = u"enter emd5"
    from pyphant.core.KnowledgeManager import KnowledgeManager
    km = KnowledgeManager.getInstance()
    if dobatch:
        import copy
        output = copy.deepcopy(input)
        index = 0
        for emd5 in input['emd5'].data:
            DummyWorker.paramEnteremd5.value = emd5
            resultDC = plug.getResult()
            km.registerDataContainer(resultDC, temporary=temporary)
            output['emd5'].data[index] = resultDC.id
            index += 1
        output.longname = longname
        output.seal()
    else:
        km.registerDataContainer(input)
        DummyWorker.paramEnteremd5.value = input.id
        output = plug.getResult()
    socket.pullPlug()
    return output

def makeSC(column_data, longnames, shortnames, longname, shortname,
           attributes={}):
    unzipped = zip(*column_data)
    assert len(unzipped) == len(longnames) == len(shortnames)
    def get_column_fc(col, ln, sn):
        try:
            from pyphant.quantities import Quantity
            unit = Quantity(1.0, col[0].unit)
            data = [quant.value for quant in col]
        except (KeyError, AttributeError):
            unit = 1
            data = col
        from numpy import array
        from pyphant.core.DataContainer import FieldContainer
        fc = FieldContainer(data=array(data), unit=unit,
                            longname=ln, shortname=sn)
        return fc
    columns = [get_column_fc(col, ln, sn) for col, ln, sn \
               in zip(unzipped, longnames, shortnames)]
    from pyphant.core.DataContainer import SampleContainer
    sc = SampleContainer(longname=longname, shortname=shortname,
                         attributes=attributes, columns=columns)
    sc.seal()
    return sc

from threading import Lock
TIMESTAMP_LOCK = Lock()
LAST_TIMESTAMP = ''
del Lock

def getModuleUniqueTimestamp():
    global TIMESTAMP_LOCK
    global LAST_TIMESTAMP
    TIMESTAMP_LOCK.acquire()
    timestamp = None
    try:
        from datetime import datetime
        while True:
            timestamp = datetime.utcnow()
            if timestamp != LAST_TIMESTAMP:
                LAST_TIMESTAMP = timestamp
                break
            else:
                from time import sleep
                sleep(.001)
    finally:
        TIMESTAMP_LOCK.release()
    return timestamp
