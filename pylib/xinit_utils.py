from pylib.syslog_utils import warn,err,info,log,WARN,ERR,INFO,warn_exp
from time import time,sleep
from pylib.du import ptb
from sys import modules
from pylib.syslog_utils.subprocess import check_output,check_call,call
from subprocess import CalledProcessError,TimeoutExpired,DEVNULL
from pylib.syslog_utils import warn,err,info,log,WARN,ERR,INFO,warn_exp,DEBUG,debug
from sys import stdout,stderr

class XinitError(Exception):
    @staticmethod
    def gen_msg(msg):
        msgline="##  ERROR: "+str(msg)+"  ##"
        headline=(len(msgline)*"#")
        footerline=headline
        return "\n"+headline+"\n"+msgline+"\n"+footerline

    def log(self,with_traceback=True):
        from traceback import format_tb
        tb = "\n".join(format_tb(self.__traceback__))
        msg=str(self) + (("\n"+ tb) if with_traceback else "")
        err(type(self).gen_msg(msg))

class Timeout(Exception):
    pass

class SkyscraperError(XinitError):
    pass

class SkyscraperNotReadyError(SkyscraperError):
    pass

class SkyscraperNotAwakeError(SkyscraperError):
    def __init__(self,*z,**zz):
        if len(z) == 1:
            super().__init__(self.gen_msg(z[0]), **zz)
        elif len(z) > 1:
            super().__init__(self.gen_msg(z[0]), *z[:1] ,**zz)
        else:
            super().__init__(self.gen_msg("skyscraper seems down and could not be awaken"),**zz)

def get_xpids(timeout=10):
    cmd = [ 'ssh', 'root@skyscraper', 'ps', '-p','1','-C', 'X', '--no-headers', '-o', 'pid']
    cmd_ssh_pipe_stop = [ 'ssh', '-O', 'exit', 'root@skyscraper' ]
    t0 = time()
    try:
        out = check_output( cmd ,stderr=stderr,timeout=timeout,loglevel=DEBUG)
    except TimeoutExpired:
        timeout = timeout - time() + t0
        call(cmd_ssh_pipe_stop,stdout=stdout,stderr=stderr,timeout=timeout,loglevel=DEBUG)
        timeout = timeout - time() + t0
        out = check_output( cmd ,stderr=stderr,timeout=timeout,loglevel=DEBUG)
    try:
        out=out.decode().split('\n')
    except AttributeError as e:
        out=[]
    pids=[]
    for line in out:
        pid=line.strip()
        if len(pid) > 0:
            pid=int(pid)
            if not pid == 1:
                pids.append(pid)
    return pids

def is_X_running_on_skyscraper(timeout=5):
    count_xpids=len(get_xpids(timeout=timeout))
    return count_xpids!=0

def not_exists_X_lockfile_on_skyscraper(timeout=40, min_timeout=21):
    """
    Returns "True" if the x lockfile does not exist on skyscraper.
    Somehow, ssh login takes aprox. 20[s].
    """
    timeout=max(min_timeout,timeout)
    cmd= ['ssh','skyscraper',"fish -c 'not test -e /tmp/.X0-lock'"]
    retval = call(cmd,stderr=stderr,stdout=stdout,timeout=timeout,loglevel=DEBUG) == 0
    return retval

def delete_X_lockfile_on_skyscraper(timeout=5):
    cmd= ['ssh','skyscraper',"fish -c 'rm /tmp/.X0-lock'" ]
    check_call(cmd,stderr=stderr,stdout=stdout,timeout=timeout,loglevel=DEBUG)

def kill_signal_X_on_skyscraper(sigstr,timeout=10):
    t0 = time()
    xpids=get_xpids(timeout=timeout)
    if len(xpids) > 0:
        cmd = [ 'ssh', 'root@skyscraper', '/bin/kill', '--signal', sigstr ] + list(str(pid) for pid in xpids)
        timeout = timeout - time() + t0
        try:
            check_call(cmd,stdout=stdout,stderr=stderr,timeout=timeout,loglevel=DEBUG)
        except CalledProcessError as e:
            print(e)
            print(cmd)
            ptb(e)

def kill_stagevise_X_on_skyscraper(timeout=15):
    t0 = time()
    kill_signal_X_on_skyscraper('QUIT',timeout=timeout)
    sleep(0.01)
    timeout = timeout - time() + t0
    kill_signal_X_on_skyscraper('TERM',timeout=timeout)
    sleep(0.01)
    timeout = timeout - time() + t0
    kill_signal_X_on_skyscraper('KILL',timeout=timeout)

def run_check_cmd_with_timeout(timeout,cmd,confirmfunc):
    t0 = time()
    if confirmfunc(timeout=timeout/5) is True:
            return True
    counter=0
    no_more_calling=False
    while time() - t0 < timeout :
        _timeout = (t0 + timeout - time()) / (4 - counter)
        try:
            if not no_more_calling:
                call(cmd,stdout=stdout,stderr=stderr,timeout = _timeout,loglevel=DEBUG)
        except TimeoutExpired:
            pass
        except PermissionError:
            no_more_calling=True
        _timeout = (t0 + timeout - time()) / (3 - counter)
        if confirmfunc(timeout = _timeout) is True:
            return True
        counter+=2
    raise Timeout()

def do_check_with_timeout(timeout,cmd,confirmfunc):
    t0 = time()
    if confirmfunc(timeout=timeout/5) is True:
            return True
    counter=0
    while True:
        _timeout = (t0 + timeout - time()) / (4 - counter)
        try:
            cmd(timeout=_timeout)
        except TimeoutExpired:
            pass
        _timeout = (t0 + timeout - time()) / (3 - counter)
        if confirmfunc(timeout = _timeout) is True:
            return True
        counter+=2
    raise Timeout()

def is_skyscraper_online(timeout=60):
    cmds=[['sudo','rc-service','skyscraper','status']]
    cmds+= [['ssh','root@skyscraper','uptime']]
    # rc_status   = call(cmds[0],stdout=stdout,stderr=stderr,timeout=int(timeout/2),loglevel=DEBUG)
    # until rc-system is fixed set to 0
    rc_status   =  0
    if rc_status == 0:
        ssh_uptime = call(cmds[1],stdout=stdout,stderr=stderr,timeout=int(timeout/2),loglevel=DEBUG)
        if ssh_uptime == 0:
            return True
        else:
            return "unknown"
    elif rc_status == 8: # starting
        return "starting"
    elif rc_status == 4: # starting
        return "stopping"
    elif rc_status == 3: # stopped
        return False
    else:
        return False

def start_restart_skyscraper(timeout=240):
    restartcmd=[ 'sudo', 'rc-service', 'cluster_esadc_skyscraper', 'restart']
    run_check_cmd_with_timeout( timeout ,restartcmd, is_skyscraper_online)

def prepare_skyscraper(timeoutmult=1,stop_running_xserver=True):
    """
    make sure skyscraper is online and ready to run the xserver
    """
    timeouts=[240*timeoutmult,60*timeoutmult,20*timeoutmult]
    try:
        do_check_with_timeout( timeouts[0], start_restart_skyscraper , is_skyscraper_online )
        # online
        # need stopped xserver
        try:
            do_check_with_timeout   (
                                    timeouts[1], kill_stagevise_X_on_skyscraper,
                                    lambda timeout=1: not is_X_running_on_skyscraper(timeout=timeout)
                                    )
        except (Timeout,TimeoutExpired):
            do_check_with_timeout   ( 
                                    timeouts[2], delete_X_lockfile_on_skyscraper,
                                    not_exists_X_lockfile_on_skyscraper
                                    )
    except (Timeout,TimeoutExpired):
        # offline
        raise SkyscraperNotAwakeError("ERROR: skyscraper did not start")

# vim: set foldlevel=0 foldnestmax=2 foldmethod=indent :
