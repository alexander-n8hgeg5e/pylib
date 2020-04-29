from os import environ

def parse_display_var():
    d=environ['DISPLAY']
    server,screen= d.split(":")
    if server.strip()=="":
        server=environ["hostnamE"]
    if server.strip()=="":
        from server import gethostname
        server=gethostname()
    return (server+":"+screen).strip()

def parse_screen_layout_env_var():
    v=environ['screen_layout']
    screens=v.split('##')
    screen_layout=[]
    for screen in screens:
        x_server,size = screen.split("#")
        size = size.split('x')
        screen_layout.append({'x_server' : x_server ,'size': size })
    return screen_layout

def parse_screen_layout_env_var_v2():
    v=environ['screen_layout_v2']
    screens=v.split('##')
    screen_layout=[]
    for screen in screens:
        x_server,geo = screen.split("#")
        x,y,size = geo.split('_')
        w,h=size.split('x')
        geo=[]
        for i in [x,y,w,h]:
            geo.append(int(i))
        geo={
                'pos' : (x,y)  ,
                'dim' : (w,h)  ,
            }
        layout={'x_server' : x_server }
        layout.update(geo)
        screen_layout.append(layout)
    return screen_layout

def parse_screen_layout_env_var_v3():
    v=environ['screen_layout_v2']
    screens=v.split('##')
    screen_layout=[]
    for screen in screens:
        x_server,geo = screen.split("#")
        x,y,size = geo.split('_')
        w,h=size.split('x')
        geo=[]
        for i in [x,y,w,h]:
            geo.append(int(i))
        geo={
                'pos' : (int(x),int(y))  ,
                'dim' : (int(w),int(h))  ,
            }
        layout={'x_server' : x_server }
        layout.update(geo)
        screen_layout.append(layout)
    return screen_layout

# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
