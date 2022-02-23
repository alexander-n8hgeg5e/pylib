
from os.path import expanduser,expandvars

def file2list(filename,decode=True):
    """
    Expands filename,reads file,strips file, returns list of lines.
    """
    if decode:
        with open(expanduser(expandvars(filename))) as f:
            data=f.read()
    else:
        with open(expanduser(expandvars(filename)),"rb") as f:
            data=f.read()
    data=data.strip()  # python strips it proper 0x0a,0x20,0x0d, maybe more
    return data.splitlines()

def file2list_v2(filename,decode=False):
    """
    Expands filename,reads,strips all lines,pops empty,returns list of lines.
    """
    if decode:
        with open(expanduser(expandvars(filename))) as f:
            data=f.read()
    else:
        with open(expanduser(expandvars(filename)),"rb") as f:
            data=f.read()
    return data2list(data)

def data2list(data):
    data = data.splitlines()
    data = [ line.strip() for line in data ]
    data = [ d for d in filter(lambda x: len(x) > 0, data ) ]
    return data
