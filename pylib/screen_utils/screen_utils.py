from .env import *
from ..xutils import xrandr_utils,xdotool_utils
from ..xutils.xrandr_utils import get_connected_outputs
from copy import deepcopy
#from ..du import dd,d1,d0

def get_output_of_active_win(active_win_id):
    """
    deprecated
    """
    return get_output_of_win(active_win_id)

def get_output_of_win(active_win_id=None):
    if active_win_id is None:
        active_win_id=xdotool_utils.get_active_win_id()

    active_win_geom =  xdotool_utils.get_win_geometry(active_win_id)
    outputs         =  xrandr_utils.get_connected_outputs()

    # match current/active win pos in the outputs
    active_win_x_pos=int(active_win_geom['pos'][0])
    # starting values
    maximum = int(outputs[0]['pos'][0])
    best_outp = outputs[0]

    for o in outputs:
        num=int(o['pos'][0])
        if  num <= active_win_x_pos:
            if maximum < num:
                maximum = num
                best_outp = o
    return best_outp

def print_win_tree(win_id,display=None):
    from Xlib.display import Display
    if display is None:
        d = Display()
    else:
        d = Display(display)
    root=d.screen().root
    child_windows = root.query_tree()._data['children']
    found = None
    done = False
    while not done:
        done = True
        for cw in child_windows:
            if cw.id == win_id:
                found=cw
                break
            else:
                add_child_windows = cw.query_tree()._data['children']
                added=False
                for child_window in add_child_windows:
                    if not child_window in child_windows:
                        child_windows.append(child_window)
                        added=True
                if added:
                    done = False
        if not found is None:
            break
    if found is None:
        raise Exception(f"No window found with the requested id: {win_id}")

    stack=[]
    def stack_geom(win,name,indent=""):
        geom = win.get_geometry()._data
        wm_name = win.get_wm_name()
        wm_class = win.get_wm_class()
        x=geom['x']
        y=geom['y']
        w=geom['width']
        h=geom['height']
        stack.append(indent+f"{name} : {x}+{y} {w}x{h} wm_name=\"{wm_name}\", wm_class=\"{wm_class}\"")
    stack_geom(found,win_id)
    parent_of = found
    indent=""
    while True:
        parent = parent_of.query_tree()._data['parent']
        if not parent == 0 :
            stack.append(indent+f"\\")
            parent_of = parent
            indent+=" "
            try:
                stack_geom(parent,parent.id,indent)
            except AttributeError:
                stack.append(parent,type(parent))
                raise
        elif parent == 0:
            stack.append(indent+f"{parent_of.id} is the ROOT window")
            break
    stack.reverse()
    il=len(indent)
    for thing in stack:
        n=0
        while thing[0] == " ":
            n += 1
            thing = thing[1:]
        print((il-n)*" "+thing)

def get_geom_of_win(win_id,display=None):
    from Xlib.display import Display
    if display is None:
        d = Display()
    else:
        d = Display(display)
    root=d.screen().root
    child_windows = root.query_tree()._data['children']
    found = None
    done = False
    while not done:
        done = True
        for cw in child_windows:
            if cw.id == win_id:
                found=cw
                break
            else:
                add_child_windows = cw.query_tree()._data['children']
                added=False
                for child_window in add_child_windows:
                    if not child_window in child_windows:
                        child_windows.append(child_window)
                        added=True
                if added:
                    done = False
        if not found is None:
            break
    if found is None:
        raise Exception(f"No window found with the requested id: {win_id}")

    geom = found.get_geometry()._data.copy()
    geom.pop('root')
    geom.pop('sequence_number')
    geom.pop('depth')
    return geom

def get_region_relative_output_index_of_window(win_id,layout=None,display=None):
    geom = get_geom_of_win(win_id,display=display)
    xpos = geom['x'] + geom['width']  / 2
    ypos = geom['y'] + geom['height'] / 2
    if layout is None:
        layout = parse_screen_layout_env_var_v3()
    region_layout = env_screen_layout_2_region_layout_v3(layout=layout)
    for i in range(len(region_layout)):
        if layout2xpos_v2( layout, i ) > xpos:
            # area at "i" is above xpos
            # so xpos belongs to i - 1
            return i-1
    # xpos belongs to rightmost one
    return i

def get_connected_output_count_at_env_layout_index(position_index,layout=None,return_x_display=False):
    """
    returns the number of the xrandr list , start is 0.
    returns tuple with second xdisplay if return_x_display
    a xrandr list belongs to a x_display.
    the env layout is the base for this func to get information
    it defines the overall layout.
    the env layout can contain more than one xserver
    each of them with multiple outputs
    implies that the outputs and the env_layout
    is physically sorted in the order of their x-positions
    and in the same direction.
    the env-layout is meant to be from left to right anyways.
    This means for example, if output has higher x pos than another
    it has to be right of the another.
    It also would work if it is left of the another but
    then the layout has to be defined from left
    to right.
    """
    if not layout:
        layout=parse_screen_layout_env_var()
    x_display=layout[position_index]['x_server']
    outputs=get_connected_outputs(x_display=x_display)
    # the pos is a position on one x-server
    pos=0
    for j in range(position_index+1):
        if layout[j]['x_server'] == x_display:
            for i in range(len(outputs)):
                    x=int(outputs[i]['pos'][0])
                    #print("pos_index:",j,"oup_pos:",x,'env_pos:',pos)
                    if pos==x and j==position_index:
                        if return_x_display:
                            return i , x_display
                        else:
                            return i
            pos+=int(layout[j]['size'][0])
    # if not found
    return None

def get_connected_output_count_at_env_layout_index_v2(position_index,layout=None,return_x_display=False):
    """
    returns the number of the xrandr list , start is 0.
    returns tuple with second xdisplay if return_x_display
    a xrandr list belongs to a x_display.
    the env layout is the base for this func to get information
    it defines the overall layout.
    the env layout can contain more than one xserver
    each of them with multiple outputs
    implies that the outputs and the env_layout
    is physically sorted in the order of their x-positions
    and in the same direction.
    the env-layout is meant to be from left to right anyways.
    This means for example, if output has higher x pos than another
    it has to be right of the another.
    It also would work if it is left of the another but
    then the layout has to be defined from left
    to right.
    """
    if not layout:
        layout=parse_screen_layout_env_var_v2()
    x_display=layout[position_index]['x_server']
    outputs=get_connected_outputs(x_display=x_display)
    # the pos is a position on one x-server
    pos=0
    for j in range(position_index+1):
        if layout[j]['x_server'] == x_display:
            for i in range(len(outputs)):
                    x=int(outputs[i]['pos'][0])
                    #print("pos_index:",j,"oup_pos:",x,'env_pos:',pos)
                    if pos==x and j==position_index:
                        if return_x_display:
                            return i , x_display
                        else:
                            return i
            pos+=int(layout[j]['dim'][0])
    # if not found
    return None

def env_screen_layout_2_region_layout(layout=None,x_display=None):
    """
    assumes that regions are in proper order,
    that means the lower regions are listed first
    in the env-screen-layout env variable.
    """
    if layout is None:
        layout=parse_screen_layout_env_var()
    if x_display is None:
        x_display=parse_display_var()
    
    regions=[]

    for screen in layout:
        if screen['x_server'] == x_display:
            # add to regions
            regions.append(screen)

    return regions

def env_screen_layout_2_region_layout_v2(layout=None,x_display=None):
    """
    assumes that regions are in proper order,
    that means the lower regions are listed first
    in the env-screen-layout env variable.
    """
    if layout is None:
        layout=parse_screen_layout_env_var_v2()
    else:
        layout=deepcopy(layout)
    if x_display is None:
        x_display=parse_display_var()
    
    regions=[]

    for screen in layout:
        if screen['x_server'] == x_display:
            # add to regions
            regions.append(screen)

    return regions

def layout2xpos(layout,index):
    """
    exspects a layout like this:
    [
    {'x_server': 'skyscraper:0', 'size': ['1360', '768']},
    {'x_server': 'skyscrapr:0', 'size': ['1920', '1080']},
    ]
    """
    pos=0
    for i in range(index):
        pos+=int(layout[i]['size'][0])
    return pos

def layout2xpos_v2(layout,index):
    """
    exspects a layout like this:
    [
    {'x_server': 'skyscraper:0', 'dim': ['1360', '768']},
    {'x_server': 'skyscrapr:0', 'dim': ['1920', '1080']},
    ]
    """
    pos=0
    for i in range(index):
        pos+=int(layout[i]['dim'][0])
    return pos


#########
## v3  ##
#########

def env_screen_layout_2_region_layout_v3(layout=None,x_display=None):
    """
    assumes that regions are in proper order,
    that means the lower regions are listed first
    in the env-screen-layout env variable.
    In v3 the regions 'pos' is relative
    """
    if layout is None:
        layout=parse_screen_layout_env_var_v3()
    else:
        layout=deepcopy(layout)
    if x_display is None:
        x_display=parse_display_var_v3()
    
    regions=[]

    for screen in layout:
        if screen['x_server'] == x_display:
            # add to regions
            regions.append(screen)

    # this is added in v3
    # make the regions 'pos' region relative
    for i in range(len(regions)):
        regions[i]['pos'] = (layout2xpos_v2( regions, i ),regions[i]['pos'][1])

    return regions

def layout2displaynr(layout=None):
    """converts the screen layout as returned from parse_screen_layout_env_var_v3
       to the display number counted in the order they appear in the env var.
    """
    if layout is None:
        layout=parse_screen_layout_env_var_v3()
    x_displays=[]
    l=[]
    for thing in layout:
        if not thing["x_server"] in x_displays:
            l.append(len(x_displays))
            x_displays.append(thing["x_server"])
        else:
            l.append(x_displays.index(thing['x_server']))
    return l

def get_focus_win(display=None):
    if display is None:
        display = parse_display_var_v3()
    from Xlib.display import Display
    display = Display(display)
    focus = display.get_input_focus()
    wf = focus._data['focus']
    return wf

def region2global_index(idx,region_xserver_string,layout=None):
    if layout is None:
        layout = parse_screen_layout_env_var_v3()
    j=0
    for i in range(len(layout)):
        if layout[i]['x_server'] == region_xserver_string:
            if idx == j:
                return i
            j+=1

def get_current_output_index(layout2displaynrlist = None,layout=None):
    """
    """
    if layout is None:
        layout = parse_screen_layout_env_var_v3()
    if layout2displaynrlist is None:
        layout2displaynrlist = layout2displaynr(layout=layout)
    display=parse_display_var_v3()
    wf=get_focus_win(display=display)
    ri=get_region_relative_output_index_of_window(wf.id,layout=layout,display=display)
    return region2global_index(ri,display,layout=layout)


# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
