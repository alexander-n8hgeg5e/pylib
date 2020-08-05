"""
du means debugutils
"""
from sys import stderr
import traceback
from re import compile 
from pprint import pprint
from shutil import get_terminal_size
from traceback import format_tb

debugstate=True
file=stderr

def d1(msg="# debugstate is True #",file=file,quiet=False):
    """enables the debug state"""
    global debugstate
    oldstate=debugstate
    debugstate=True
    if not quiet and debugstate != oldstate and not msg is None:
        print(msg,file=file)

def d0(msg="# debugstate is False #",file=file,quiet=False):
    """disables the debug state"""
    global debugstate
    oldstate=debugstate
    debugstate=False
    if not quiet and debugstate != oldstate and not msg is None:
        print(msg,file=file)

def dd(thing,file=file):
    """
    print the thing to stderr if debugstate
    prints some add information
    name dd is short for easy debugging during coding
    d would interfer often with local dict var names
    """
    if debugstate:
        stack = traceback.extract_stack()
        filename, lineno, function_name, code = stack[-2]
        var_name = compile(r'\((.*?)\).*$').search(code).groups()[0]

        start            = var_name + ' ='
        string_thing     = str(thing)
        len_string_thing = len(string_thing)
        s0               = start+" "+string_thing
        ts = get_terminal_size()[0]
        if  len_string_thing > ts:
            print(  start, file=file   )
            pprint( thing, stream=file )
        elif len(s0) + 4 < ts:
            print( s0, file=file   )
        else:
            print( start, file=file )
            print( 4*" " + string_thing , file=file )

def ptb(e,file=stderr):
    for line in format_tb(e.__traceback__):
        print(line,file=file)
    print(e,file=file)

def ftb_list(e):
    return format_tb(e.__traceback__) + [str(e)]

def ftb(e):
    return "\n".join(ftb_list(e))


from collections import OrderedDict as Od
def ddd(thing):
    stack = traceback.extract_stack()
    for s in stack:
        filename, lineno, function_name, code = s
        if filename == '/var/src/conkyconfpy/conkyconfpy.py':
            d = Od  (
                        {
                        'lineno'           : lineno  ,
                        'function_name'    : function_name,
                        'code'             : code,
                        }
                    )
            pprint(d)


def dddd(thing):
    stack = traceback.extract_stack().extract(0)
    print(dir(stack[-1]))
    help(traceback.walk_stack)
    for s in traceback.walk_stack(stack[-1]):
        pprint(s)
