import sys
sys.path.append('../src/workers/OSC/OSC/tests')
import grammar 

definitions = {}
for key,value in grammar.__dict__.iteritems():
    if hasattr(value,'__doc__') and (key.startswith('p_')):
        print value.__doc__
    if key.startswith('t_'):
        if type(value) in (type(u'a'),type('a')):
            definitions[key] = value
        else:
            definitions[key] = value.__doc__
for key,value in definitions.iteritems():
    print key,value

