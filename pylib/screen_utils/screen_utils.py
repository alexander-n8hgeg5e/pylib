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
        x_display=parse_display_var()
    
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

# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
