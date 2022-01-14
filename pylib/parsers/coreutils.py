#!/usr/bin/env python3
from re import sub

def parse_id(txt):
    uid, gid, groups = txt.split(' ')
    def do_one_of3(one):
        what, things = one.split('=')
        return { what : things.split(',') }
    def do_element(e):
        e = e.split('(')
        return e[1].strip(r')'), int(e[0])
    data={}
    for thing in (uid,gid,groups):
        data.update(do_one_of3(thing))
    for k in data.keys():
        data[k] = dict( (i for i in do_element(x)) for x in data[k] )
    return data
