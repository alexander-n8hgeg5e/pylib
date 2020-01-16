from subprocess import call,Popen,PIPE,DEVNULL
from re import sub
from os import environ

def get_current_desktop():
    p=Popen([ 'xdotool', 'get_desktop' ],stdout=PIPE)
    return p.stdout.read().decode().strip()
    

def get_root_win_geometry():
    p=Popen([ 'xdotool', 'search',  '--maxdepth', '0', '.*', 'getwindowgeometry' ],stdout=PIPE,stderr=DEVNULL)
    txt_lines=p.stdout.read().decode().split('\n')
    return extract_geom(txt_lines)

def get_root_win_id():
    p=Popen([ 'xdotool', 'search',  '--maxdepth', '0', '.*' ], stdout=PIPE, stderr=DEVNULL)
    txt_lines=p.stdout.read().decode().split('\n')
    found=""
    for line in txt_lines:
        line=line.strip()
        if found =="" and line != "":
            found=line
        elif found != "" and line !="":
            raise Exception("Error: there should be only one line with something not stripable by strip() without args")
    return int(found)

def extract_geom(txt_lines):
    data={}
    for line in txt_lines:
        if line.find("Position:") != -1:
            pos=sub("(.*)[(].*[)]","\\1",line).split(":")[1].strip().split(",")
            data.update({'pos':pos})
        if line.find("Geometry:") != -1:
            geo=line.split(":")[1].strip().split("x")
            data.update({'geo':geo})
        ks=data.keys()
        if 'pos' in ks and 'geo' in ks:
            break
    return data

def get_active_win_id():
    p=Popen(['xdotool', 'getactivewindow'],stdout=PIPE)
    winid=p.stdout.read().strip().decode()
    p.terminate()
    return winid

def get_win_geometry(winid,x_display=None):
    cmd=['xdotool' , 'getwindowgeometry', winid ]
    if x_display:
        env=environ.copy()
        env.update({'DISPLAY':x_display})
        p=Popen(cmd,stdout=PIPE,env=env)
    else:
        p=Popen(cmd,stdout=PIPE)
    retcode=p.wait()
    if retcode==0:
        geom=p.stdout.read()
        p.terminate()
        geomlines=geom.decode().split("\n")
        return extract_geom(geomlines)
    else:
        return None

def find_window(*z,wname=".*",wclass=".*",wclassname=".*", env=None, **zz):
    di={'wclass':wclass,'wclassname':wclassname,'wname':wname}
    d={}
    for k,v in di.items():
        if v != ".*":
            d.update({k:v})
    d2={}
    for k,v in d.items():
            cmd=['xdotool','search','--'+k[1:],d[k]]
            if not env is None:
                p=Popen(cmd,stdout=PIPE,env=env)
            else:
                p=Popen(cmd,stdout=PIPE)
            data=p.stdout.read().strip().decode()
            p.terminate()
            datalines=data.split("\n")
            data=[]
            for v in datalines:
                try:
                    data.append(int(v.strip()))
                except:
                    pass
            d2.update({k: {'data':data,'search_string': d[k]}})
    l3=[]
    l12=list(d2.values())
    v1=l12[0]
    if len(l12) > 1:
        l2=l12[1:]
    else:
        return v1['data']
    if len(v1['data']) == 0:
        return []
    for i in v1['data']:
        append=True
        for v2 in l2:
            if not i in v2['data']:
                append=False
        if append:
            l3.append(i)
    return l3





