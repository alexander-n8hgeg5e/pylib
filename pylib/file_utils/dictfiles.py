from os import mkdir
from os.path import exists
from os import listdir
from os.path import isfile,isdir,abspath
from re import match
from pprint import pprint
from collections import OrderedDict as Od

def write(d,path=".",max_data_len=64,silent_skip=False):
    for k,v in d.items():
        if not type(v) is dict:
            data=str(v).encode()
            if len(data) > max_data_len and not silent_skip:
                raise Exception("ERROR: data len limit reached. file is too big. \n file=\"{}\"".format(k))
            with open(path+"/"+k,mode="wb") as f:
                f.write(data[:max_data_len])
        else:
            path=path+"/"+k
            if not exists(path):
                mkdir(path)
            write(v,path=path)


def read(path=".",regex=".*",max_data_len=64,silent_skip=False ,nostrip=False,noconv=False, recursive=True):
    """
    """
    dirlist=listdir(path)
    l=[]
    data={}
    for thing in dirlist:
        if isfile(path+"/"+thing) and match(regex,path+"/"+thing):
            l.append(thing)
        elif recursive and isdir(path+"/"+thing) and match(regex,path+"/"+thing):
            data.update( { thing : read( path=path + "/" + thing ,regex=regex,max_data_len=max_data_len,silent_skip=silent_skip,noconv=noconv,nostrip=nostrip)})
    l.sort()
    for k in l:
        p = abspath(path + "/" + k)
        with open(p) as f:
            try:
                d=f.read(max_data_len + 1)
            except OSError:
                print(f"failed to read path \"{p}\"")
            if len(d) > max_data_len and not silent_skip:
                raise Exception("ERROR: data len limit reached. file is too big. \n file=\"{}\"".format(k))
            d=d[:max_data_len]
            if not nostrip:
                d = d.strip()
            if not noconv:
                if match("^[0-9]+$",d):
                    d = int(d)
                elif match("^[0-9]*[.][0-9]*$",d):
                    d = float(d)
            data.update({k:d})
    return data
