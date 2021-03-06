from subprocess import Popen,check_call
from signal import SIGCONT,SIGSTOP
from time import sleep
from sys import stderr
from pylib.du import dd
from types import FunctionType
from os.path import sep as psep
from os import getpgid,killpg,setpgid,getppid,getpid,kill
from psutil import pids
from warnings import warn
from pylib.stat_utils import Pid_throttler

class Cmdrunner():
    def __init__(self,cmds,*z,**zz):
        self.cmds=cmds
        self.z=z
        self.zz=zz

    def run(self,dry_run=False):
        for cmd in self.cmds:
            if type(cmd[0]) is FunctionType:
                func,args,kwargs=self._prepare_cmd_and_args(cmd)
                if not dry_run:
                    func(*args,**kwargs)
                else:
                    print('dry_run',cmd[0],args,kwargs,file=stderr)
            else:
                cmd0,args,kwargs=self._prepare_cmd_and_args(cmd)
                if not dry_run:
                    check_call(cmd0,*args,*kwargs)
                else:
                    print('dry_run('+str(cmd0)+', '+str(*args)+', '+str(', '.join(' = '.join(zip((str(j),str(k)) for (j,k) in kwargs.items())))),file=stderr)
    def _prepare_cmd_and_args(self,cmd):
        args=[]
        kwargs={}
        if not type(cmd[0]) is str:
            for e in cmd[1:]:
                if type(e) is dict:
                    kwargs.update(e)
                else:
                    args+=[e]
            cmd=cmd[0]
        kwargs.update(self.zz)
        args+=self.z
        return cmd,args,kwargs

class ConditionRunner():
    """
    ConditionRunner runs the cmd and stops it one of the supplied condition
    check functions returns True.
    """
    STARTED=0
    STOPPED=1
    def __init__(self,popen_cmd,conditions,ioprio="c3",niceness="19",popenargs=[],popenkwargs={},polltime=5,debug=False,verbose=False):
        self.cmd=popen_cmd
        self.conditions=conditions
        self.ioprio=ioprio
        self.niceness=niceness
        self.popenargs=popenargs
        self.popenkwargs=popenkwargs
        if 'start_new_session' in self.popenkwargs.keys():
            warn(   
                    "WARNING: the kwarg \"start_new_session\" is set to True\n"
                    "in all cases."
                )
        self.popenkwargs.update({'start_new_session':False})
        self.polltime=polltime
        self.state=None
        self.pid=getpid()
        self.pgid=None
        self.checkstats={'lastchecks':[],'last_periodes':[],'avg_period':None}
        self.interp_counter=0
        self.interp_interv=5
        self.debug=debug
        self.verbose=verbose if not debug else True
    def _update_pids_(self):
        self.pids=[]
        for pid in pids():
            try:
                pgid=getpgid(pid)
            except ProcessLookupError:
                continue
            if pgid==self.pgid and not pid==self.pid:
                self.pids.append(pid)

    def _stop_pids_(self):
        if self.state==self.STOPPED:
            return
        if self.debug:
            print("sending SIGSTOP...",file=stderr)
        self._update_pids_()
        poppids=[]
        for pid in self.pids:
            try:
                kill(pid,SIGSTOP)
            except ProcessLookupError:
                poppids.append(pid)
        self.state=self.STOPPED
        for pid in poppids:
            try:
                self.pids.remove(poppids)
            except ValueError as e:
                warn(str(e))
    def _start_pids_(self):
        if self.state==self.STARTED:
            return
        if self.debug:
            print("sending SIGCONT...",file=stderr)
        for pid in self.pids:
            try:
                kill(pid,SIGCONT)
            except ProcessLookupError:
                warn("process vanished: "+str(pid))
                pass
        self.state=self.STARTED

    def check_wrapper(self,checkfunc):
        self.interp_counter+=1
        if self.debug:
            pprint(self.checkstats,file=stderr)
        lc=self.checkstats['lastchecks']
        if len(lc) < 25:
            check_result=checkfunc()
            self.checkstats['lastchecks'].append(check_result)
            return check_result
        else:
            if len(lc) > 26:
                self.lastchecks.checkstats=lc[-26:-1]
            # update periodes
            change=[None]*3
            j=0
            while not change[-1] == True and change[-3] == True:
                for i in range(1,len(lc)):
                    if lc[i] != lc[0]:
                        change.append(i)
                        break
                lc=lc[i:]
                j+=1

            if change[-1] == True and change[-3] == True:
                self.checkstats['last_periodes'].append(change[2]-change[0])
                self.checkstats['lastchecks']=self.checkstats['lastchecks'][1:]
            
            # update average periodes
            lp=self.checkstats['last_periodes']
            if len(lp) > 26:
                self.lastchecks['periodes']=lp[-26:-1]
            if len(lp) > 24:
                # update avg_periodes
                avgp=self.checkstats['avg_period']
                avg_periodes=sum(lp)/len(lp)
                self.checkstats['avg_period']=avg_periodes
                
                last_change=None
                # get last change
                lc=self.checkstats['lastchecks']
                for i in range(-2,-len(lc)-1,-1):
                    if lc[i] != lc[-1]:
                        last_change=len(lc)-i
                        break
                if not self.interp_counter % self.interp_interv == 0 \
                        and not last_change is None \
                        and last_change == round(self.checkstats['avg_period']):
                    self.checkstats['lastchecks'].append(True)
                    if self.debug:
                        print("infering check result: True",file=stderr)
                    return True
                else:
                    check_result=checkfunc()
                    self.checkstats['lastchecks'].append(check_result)
                    return(check_result)
                
    def run(self):
        cmd=['nice',"-n"+str(self.niceness),'ionice',"-"+self.ioprio]+self.cmd
        self.p=Popen(cmd,*self.popenargs,**self.popenkwargs)
        self.pgid=getpgid(self.p.pid)
        while self.p.poll() is None:
            # is running, not done
            startit=True
            for check in self.conditions:
                if check():
                    self._stop_pids_()
                    startit=False
            if startit and self.state == self.STOPPED:
                self._start_pids_()
            sleep(self.polltime)

    def __del__(self):
        self.p.terminate()
        self.p.kill()

class ConditionRunThrottler():
    """
    ConditionRunner runs the cmd and throttles it,
    if one of the supplied condition check functions returns True.
    The method is sending sigstop and sigcont signals.
    update_pids needs to be called and adds
    all the pids of the own process group except the
    pid running this code.
    """
    def __init__(
                    self, popen_cmd, conditions, ioprio="c3", niceness="19",
                    popenargs=[], popenkwargs={},
                    control_interval = 5,
                    debug = False,verbose = False ,
                    update_divider=10
                ):
        self.cmd=popen_cmd
        self.conditions=conditions
        self.ioprio=ioprio
        self.niceness=niceness
        self.popenargs=popenargs
        self.popenkwargs=popenkwargs
        self.update_divider=update_divider
        if 'start_new_session' in self.popenkwargs.keys():
            warn(   
                    "WARNING: the kwarg \"start_new_session\" is set to True\n"
                    "in all cases."
                )
        self.popenkwargs.update({'start_new_session':False})
        self.control_interval=control_interval
        self.pid=getpid()
        self.pgid=getpgid(self.pid)
        self.level=0
        self.pt=Pid_throttler(verbose=verbose,debug=debug)
        self.debug=debug
        self.verbose=verbose if not debug else True

    def _update_pids_(self):
        if self.debug:
            print("updateing pids...")
        for pid in pids():
            try:
                pgid=getpgid(pid)
            except ProcessLookupError:
                continue
            if pgid==self.pgid and not pid==self.pid:
                self.pt.add_pid(pid)
                if self.debug:
                    print("added pid: "+str(pid))

    def _brake_(self):
        if self.level < 9:
            self.level+=1
            if self.debug:
                print("level--",file=stderr)
        self.pt.throttle(self.level,pretend=False)

    def _accel_(self):
        if self.level > 0:
            self.level-=1
            if self.debug:
                print("level++",file=stderr)
        self.pt.throttle(self.level,pretend=False)

    def run(self):
        cmd=['nice',"-n"+str(self.niceness),'ionice',"-"+self.ioprio]+self.cmd
        self.p=Popen(cmd,*self.popenargs,**self.popenkwargs)
        self.pgid=getpgid(self.p.pid)
        self._update_pids_()
        counter=0
        while self.p.poll() is None:
            counter+=1
            # is running, not done
            for check in self.conditions:
                if check():
                    self._brake_()
                else:
                    self._accel_()
            sleep(self.control_interval)
            if counter % self.update_divider == 0:
                self._update_pids_()
        return self.p.returncode

    def __del__(self):
        self.pt.__del__()
        self.p.terminate()
        self.p.kill()

#def get_cpu_stats():
#    field_names=[ 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice' ]
#    with open("/proc/stat") as f:
#        data=f.read()
#    lines=data.split("\n")
#    for line in lines:
#        if line[:4] == "cpu ":
#            cpustat_line=line[4:].strip()
#            break
#    cpustat_fields=cpustat_line.split(" ")
#    cpustats={}
#    for name,field in zip(field_names,cpustat_fields):
#        cpustats.update({name:int(field)})
#
#    _sum=cpustats['user']+cpustats['system']+cpustats['iowait']+cpustats['idle']
#    for k,v in cpustats.items():
#        cpustats.update({k:v/_sum})
#    cpustats.update({'sum':_sum})
#    return cpustats

# vim: set foldlevel=0 foldmethod=indent foldnestmax=2 :
