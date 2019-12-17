from pprint import pprint,pformat
from pylib.du import dd,d0,d1
from copy import copy
from re import sub
from os.path import exists,isfile
d0()
def do_all_dir  (
                    thing,
                    doable,
                    *doargs,
                    subregs={},
                    rec=True,
                    namespace_path="",
                    exclude=[],
                    write_exclude_file='/tmp/pylib-module-tools.py-exclude-file-write',
                    read_exclude_file='/tmp/pylib-module-tools.py-exclude-file-read',
                    root=True, **zz ):
    """
    This code was created haphazardly,
    by adding code wheresoever the cursor was.
    Does for all in dir of thing the doable.
    The first arg is the object found in dir.
    "doargs", if they are of type str,
    get expanded by sub(subreg_name,actual_name,doarg).
    "actual_name" is the attributes name.
    """
    if type(read_exclude_file) is str and exists(read_exclude_file) and isfile(read_exclude_file):
        with open(read_exclude_file) as rf:
            data=rf.read()
        data=data.split("\n")
        for line in data:
            exclude.append(line.strip())
    try:
        exclude__=  [
                        "base",
                        "abstractmethods",
                        "call",
                        "bases",
                        "class",
                        "delattr",
                        "annotations",
                        "closure",
                    ]
        exclude_=   [
                    ]
        orig_z  = copy([thing,doable,*doargs])
        orig_zz = copy({'subregs':subregs,'rec':True,'namespace_path':"",'exclude':exclude,**zz})
        for x in exclude__ :
            exclude.append("__"+x+"__")
        for x in exclude_ :
            exclude.append("_"+x+"_")

        for i in dir(thing):
            if i in exclude:
                continue
            aa=[]
            for a in doargs:
                if type(a) is str and not subregs is None:
                    for srk,srv in subregs.items():
                        try:
                            g=dict(globals())
                            g.update(dict(locals()))
                            aa.append(sub(srv,g[srk],a))
                        except KeyError:
                            pprint(locals()['namespace_path'])
                            pprint(namespace_path)
                            raise
                else:
                    aa.append(a)
            try:
                o=getattr(thing,i)
            except AttributeError:
                print   (
                        'Failed to get attribute "'+i+'" from "'+str(thing)+'".\n'
                        'namespace_path='+namespace_path
                        )
                continue
            if rec:
                if hasattr(o,'__dir__'):
                    dd(str("# path="+namespace_path+"."+i+"\n####"))
                    ns_sp=namespace_path.split(".")
                    max_chainlen=10
                    min_chainlen=5
                    chains=[]
                    rj=range(min_chainlen, max_chainlen+1)
                    rk='range(int((len(ns_sp)-j)/j))'
                    for j in rj:
                        chains.append([])
                        for k in eval(rk):
                            oo=ns_sp[k:k+j]
                            dd(type(oo))
                            dd(len(oo))
                            dd(oo)
                            dd(chains)
                            dd(chains[j-min_chainlen])
                            chains[j - min_chainlen].append(oo)
                            dd(chains)
                    #pprint(chains)
                    for isc,subchains in zip(range(len(chains)),chains):
                        lic=len(subchains)
                        for ic,chain in zip(range(len(subchains)),subchains):
                            #print(str([j,k*j,i])+"-"+str(chains[j - min_chainlen][k*j:(k*j)]))
                            for wide in range(1,len(subchains)+1):
                                if lic-ic <= wide:
                                    continue
                                l0=chain
                                l1=subchains[ic+wide]
                                if type(l0[0]) is list:
                                    dd(print(chains))
                                    dd(l0)
                                    dd(l0[0])
                                    raise Exception("ERROR: should be string, is list")
                                if len(l0)>=min_chainlen and l0==l1:
                                    print("found")
                                    l3={}
                                    for s3 in l0:
                                        try:
                                            if s3 not in l3.keys():
                                                l3.update({s3:1})
                                            else:
                                                l3[s3]+=1
                                        except TypeError as e:
                                            print(str(e)+"\n"+str(l0))
                                            raise
                                    maxval=max(l3.values())
                                    for l3k,l3v in l3.items():
                                        if l3v==maxval:
                                            maxkey=l3k
                                            if maxkey not in exclude:
                                                print("adding to exclude: "+ maxkey)
                                                exclude.append(maxkey)
                                                orig_zz.update({'exclude':exclude})
                                                orig_zz.update({'root':False})
                                                return do_all_dir(*orig_z,**orig_zz)
                                    #raise Exception (
                                    #                "ERROR: probably recursion detected"
                                    #                 +pformat(l0)+"\n==\n"+pformat(l1)
                                    #                 +"\n"+str(k*j)+" "+str(k*j+j)+"=="+str(k*j+h)+" "+str(k*j+h+j)
                                    #                )
                        
                                        
                    do_all_dir(o,doable,*doargs,subregs=subregs,rec=rec,
                                namespace_path=namespace_path+"."+i,root=False,
                                **zz)
            doable(o,*aa,**zz)
    finally:
        if root:
            with open(write_exclude_file,"at") as f:
                for item in exclude:
                    f.write(item+"\n")
