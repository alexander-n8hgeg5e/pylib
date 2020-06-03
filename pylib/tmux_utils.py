from subprocess import check_call
from os import isatty,stdin

def rename_session_if_tmux_tty(newname):
    if isatty(stdin):
        # check if tmux connection ok
        tmux_conn_ok=False
        try:
            cmd=['tmux','list-windows']
            check_call(cmd)
            tmux_conn_ok=True
        except:
            pass
        if tmux_conn_ok:
            cmd=['tmux','rename-session',str(newname)]
            check_call(cmd)
        
    
