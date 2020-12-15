from re import sub
from functools import reduce
from pylib.syslog_utils import err
from pprint import pformat
from traceback import format_tb
from collections import OrderedDict

def update_nested_dict(d1, d2):
    """
    Updates d1 with d2.
    The dict datatype wins over other datatypes.
    """
    if len(d2) > 0:
        d1keys=d1.keys()
        for k2 in d2.keys():
            def do():
                d1[k2]=d2[k2]
            if k2 in d1keys:
                if type(d1[k2]) is dict and type(d2[k2]) is dict:
                    # Key points to 2 dicts, need to go deeper.
                    d1[k2] = update_nested_dict(d1[k2] , d2[k2] )
                elif type(d2[k2]) is dict():
                    # Update existing key in d1 with a dict.
                    # The dict wins over other datatypes here.
                    do()
                else:
                    # Don't overwrite a dict, do nothing.
                    pass
            else:
                # Because key is not in d1,
                # there is no doubt that "do" is the right choice. 
                do()
        return d1
    else:
        return d1

def get_item_from(thing, mapList):
    return reduce(get_from, mapList, thing)

def set_item_in(thing, mapList, value):
    set_in(get_from( get_item_from( thing, mapList[:-1]), mapList[-1] ),mapList[-1],value)

def get_from( thing, what ):
    if hasattr(thing,'__dict__'):
        return(thing.__dict__[what])
    elif hasattr(thing,'__getitem__'):
        #print(thing,what)
        try:
            return thing[what]
        except KeyError as e:
            err("WARNING: KeyError: Key: "+pformat(what)+"\nException:"+str(e)+"\n"+"\n".join(format_tb(e.__traceback__))+"\nDict: "+ pformat(thing))
            raise e

def set_in(thing, what ,val):
    if hasattr(thing,'__setattribute__'):
        thing.__setattribute__(what,val)
    elif hasattr(thing,'__setitem__'):
        thing[what]=val
    else:
        raise Exception("missing __setattribute__ or __setitem__ in "+thing.__repr__())

def format(d,dict_format):
    #for k,v in d.items():
    #    if k.find("enable") != -1:
    #        print("k={},type(k)={}, v={},type(v)={}".format(k,type(k),v,type(v)))
    lines=[]
    for line_format in [lf for lf in dict_format.split("\n")]:
        try:
            line_format_dict_prep=sub("{",'"{',line_format)
            line_format_dict_prep=sub("}",'}"',line_format_dict_prep)
            line_format_dict = eval("OrderedDict({" +line_format_dict_prep+ "})")
            #print(line_format_dict.items())
            values=[]
            for k in line_format_dict.keys():
                values.append(d[k])
            try:
                lines.append(line_format.format(*values))
            except ValueError as e:
                from sys import stderr
                print(e)
                print("ERROR:",line_format,file=stderr)
            except IndexError as e:
                from sys import stderr
                pprint(line)
                print(e)
                print("ERROR:",line_format,file=stderr)
        except Exception as e:
            if type(e) in [ValueError,SyntaxError]:
                lines.append(line_format)
                continue
    return lines

