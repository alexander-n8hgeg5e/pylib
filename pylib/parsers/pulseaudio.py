from .indent import IndentationParser
from pylib.dict_utils import update_nested_dict as ud
from pylib.dict_utils import *
from re import match

class PulseaudioctlParser():
    ITERTYPES=(list,)
    DATATYPES=(str,bytes)

    @staticmethod
    def parse_key_value(i):
        for sep in ["=",":"," "]:
            if sep in i:
                a,b=i.split(sep)
                break
        a=a.strip()
        b=b.strip()
        return {a:b}

    def __init__(self,data):
        self.data=data
        #t=type(data)
        #if t is bytes:
        #    self.data=data.decode()
        #elif t is str:
        #    self.data=data
        #else:
        #    raise TypeError("Unsupported type: {}".format(t))

    @staticmethod
    def is_root(s):
        if s[-1] == ":":
            return True
        if match(".*[ ][0-9]+[#]$",s):
            return True

        return False
    @staticmethod
    def _do(iterable,root="root"):
        iter_todo=[]
        items={}
        root=None
        li=len(iterable)
        #print("li={}".format(li))
        for i in range(len(iterable)):
            #print('iterable[{}] = "{}"'.format(i,iterable[i]))
            if type(iterable[i]) in PulseaudioctlParser.ITERTYPES:
                iter_todo.append(iterable[i])
            elif type(iterable[i]) in PulseaudioctlParser.DATATYPES:
                #print("datatype")
                if i == 0 and PulseaudioctlParser.is_root(iterable[i]):
                    #print("root=",pi)
                    root=iterable[i].strip(":")
                else:
                    kv = PulseaudioctlParser.parse_key_value(iterable[i])
                    items.update(kv)
                    #print("data=",pi)
            else:
                raise TypeError()
        #print('return\n    root="{}"\n    iter_todo="{}"\n    items="{}"'.format(root,iter_todo,items))
        return root,iter_todo,items

    def parse(self,maxlevel=20):
        ip=IndentationParser(self.data)
        ip.parse()
        from pprint import pprint
        pprint(ip.data)
        ip.data=[ip.data[-1]]
        level=0
        path=[]
        root,iter_todo,items = self._do(ip.data)
        counter=0
        while not len(iter_todo) == 0:
            counter+=1
            #print("len iter_todo =",len(iter_todo))
            #pprint("iter_todo = {}".format(iter_todo))
            #print()
            i=iter_todo.pop()
            #print("i=",i)
            level+=1
            if not root in ("root",None):
                path.append(root)
            more_iter_todo=[]
            root,_more_iter_todo,more_items = PulseaudioctlParser._do(i)
            #print(root,_more_iter_todo,more_items)
            more_iter_todo+=(_more_iter_todo)
            for k,v in more_items.items():
                print(k)
                if not k is None:
                    p=path+[k]
                if counter == 1:
                    if None in p:
                        print("none found:",items,path,k,v)
                    print("set item:",items,p,v)
                set_item_in(items, p , v)
            if level <= maxlevel:
                #print("more_iter_todo={}".format(more_iter_todo))
                iter_todo+=more_iter_todo
            print("len iter_todo =",len(iter_todo))
        return items
