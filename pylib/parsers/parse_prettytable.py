# coding: utf-8
from re import sub
from csv import reader
from pprint import pprint
from prettytable import PrettyTable

def read_csv(iterable):
    return list(reader(iterable,dialect='unix'))


def parse(filename,cornerchar='+'):
    with open(filename) as f:
        data=f.read()
    datalines=data.split('\n')
    datalines_=[]
    for line in datalines:
        if len(line) == 0:
            continue
        if not line[0]==cornerchar:
            line=line[1:-1]
            line=sub('[ ]*[|][ ]*','","',line)
            line='"'+line+'"'
            datalines_.append(line)
    datalines=datalines_
    pydata=read_csv(datalines)
    field_names=[]
    for field in pydata[0]:
        field_names.append(field.strip())
    pt=PrettyTable(field_names=field_names)
    for row in pydata[1:]:
        pt.add_row(prepare_row(row))
    return pt

def prepare_row(row):
    return_row=[]
    for field in row:
        field_=field.strip()
        return_row.append(field_)
    return return_row
        
