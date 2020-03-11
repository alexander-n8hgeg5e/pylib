
from os.path import expanduser,expandvars

def file2list(f):
    with open(expanduser(expandvars(f))) as ff:
        kwd_data=ff.read()
    kwd_data=kwd_data.strip("\n")
    return kwd_data.split("\n")
