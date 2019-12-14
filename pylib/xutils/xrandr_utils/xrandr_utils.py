from subprocess import check_output,Popen,getoutput
from subprocess import call
from os import environ as env
from functools import cmp_to_key
from os import listdir,mkdir,unlink
from sys import exit,argv
from warnings import warn
from pylib.screen_utils.env import parse_screen_layout_env_var
from collections import OrderedDict

def startswith(string,startstring):
    return string[0:len(startstring)] == startstring

def endswith(string,endstring):
    return string[-len(endstring):] == endstring

def parse_layout(x_display=None):
    """
    returns the layout
    layout is list of OrderedDicts , one per "xorg-screen",
    the ordered dicts are containing dicts of outputs.
    outputs and xorg-screens are in order of xrandr outp
    """
    if x_display:
        pass_env=env.copy()
        pass_env.update({"DISPLAY":x_display})
        lines = check_output([ 'xrandr' ],env=pass_env).decode().split("\n")
    else:
        lines = check_output([ 'xrandr' ]).decode().split("\n")

    screen_lines=__parse_screen_lines_stage1(lines)

    layout=__parse_screen_lines_stage2(screen_lines)

    return layout

def get_connected_outputs_layout(x_display=None):
    """
    returns a list of dicts that are the connected outputs of one "x-window-screen"
    propably the will be only one list entry containing a dict with multiple outputs
    this means x-screen 0 has the connected outputs that are in the dict
    """
    l=parse_layout(x_display=x_display)
    ret=[]
    for x_screen in l:
        d={}
        for k,v in x_screen.items():
            if v['connected']:
                d.update({k:v})
        ret.append(d)
    return ret

def get_connected_outputs(x_display=None):
    """
    returns one list with connected outputs no matter to what x-screen they belong
    no output names, only the outputs, what means their data
    data is pos size, stuff parsed from xrandr output
    order is the one of xrandr outp
    """

    l=parse_layout(x_display=x_display)
    ret=[]
    for x_screen in l:
        for k,v in x_screen.items():
            if v['connected']:
                ret.append(v)
    return ret

def get_connected_outputs_x_sorted(x_display=None):
    """
    returns one list with connected outputs no matter to what x-screen they belong, sorted in order low x pos to high x pos
    no output names, only the outputs, what means their data
    data is pos size, stuff parsed from xrandr output
    """
    outp=get_connected_outputs(x_display=x_display)
    outp.sort(key=lambda outp: outp['pos'][0])
    return outp

        

def __prepare_lines(outp):
    """
    does nothing useful yet
    """
    lines=[]
    for i in outp:
        lines.append(i)
    return lines

def __parse_screen_lines_stage1(lines):
    """
    ret list of screens containing lists with corresponding lines
    the lines are in the order of the xrandr output
    """
    screen_lines = []
    l=[]
    capture=False
    for line in lines:
        if startswith(line,"Screen"):
            capture = True
            if len(l) > 0:
                 screen_lines.append(l)
                 l=[]
        else:
            if capture and len(line) > 0 and line[0]!=" ":
                l.append(line)
    screen_lines.append(l)
    return screen_lines

def __parse_screen_lines_stage2(screen_lines):
    """
    Parses stuff from (xrandr) screen lines and puts into layout.
    layout and screen_lines are lists with same lenght and
    corresponding entries at same index position.
    all entries are in the order of the xrandr outp
    so this func needs to use OrderedDict
    """
    layout=__prepare_layout_list(screen_lines) # empty skeleton , a list containing empty ordered dicts 
    for i in range(len(layout)):
        for j in screen_lines[i]:
            if j[0] is not " ":
                d={}
                words = j.split(" ")
                output_name = words[0]
    
                connected = (words[1]== "connected")
                d.update({ "connected" : connected })
    
                if words[2] == "primary":
                    d.update({"primary": True})
                    pos_str= words[3]
                    rotate =  (words[4].strip() == "left" or words[4].strip() == "right")
                else:
                    d.update({"primary": False})
                    pos_str= words[2]
                    rotate = (words[3].strip() =="left" or words[3].strip() == "right")

                d.update({"rotate" : rotate})
    
                pos = tuple(pos_str.split("+")[1:])
                d.update({ "pos" : pos })
    
                size = tuple(pos_str.split("+")[0].split('x'))
                d.update({ "size" : size })
    
                layout[0].update( { output_name : d } )
    return layout

def __prepare_layout_list(screen_lines):
    """
    Takes the len of the screen lines and
    makes a list of equal length,
    that is filled with empty dicts 
    A list entry is a dict that will
    contain the information of the "xrandr_output_screen".
    look in xrandr manual to find out what that means.
    """
    layout=[]
    for i in range(len(screen_lines)):
        layout.append( OrderedDict() )
    return layout

def get_outputs_count(*z,**zz):
    """
    returns the "connected" outputs count
    """
    warn("func is deprecated use 'get_connected_outputs_layout'",DeprecationWarning,stacklevel=2)
    return get_connected_outputs_count(*z,**zz)

def get_connected_outputs_count(layout,connected_ones=True):
    count=0
    for screen in layout:
        for outp in screen.keys():
            if screen[outp]['connected']:
                count= count + 1
    return count 

def outp_is_right_of_outp(outp1,outp2):
    """
    same screen
    """
    pos1=outp1['pos'][0]
    pos2=outp2['pos'][0]
    return pos1 < pos2
