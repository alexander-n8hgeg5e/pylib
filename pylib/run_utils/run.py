from subprocess import Popen
from signal import SIGCONT,SIGSTOP
from time import sleep
from pylib.du import dd
from types import FunctionType
from os.path import sep as psep

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
                    print('dry_run',cmd[0],args,kwargs)
            else:
                cmd0,args,kwargs=self._prepare_cmd_and_args(cmd)
                if not dry_run:
                    check_call(cmd0,*args,*kwargs)
                else:
                    print('dry_run('+str(cmd0)+', '+str(*args)+', '+str(', '.join(' = '.join(zip((str(j),str(k)) for (j,k) in kwargs.items())))))
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
    def __init__(self,cmd,conditions,ioprio="c3",niceness="19",popenargs=[],popenkwargs={},polltime=5):
        self.cmd=cmd
        self.conditions=conditions
        self.ioprio=ioprio
        self.niceness=niceness
        self.popenargs=popenargs
        self.popenkwargs=popenkwargs
        self.polltime=polltime
        self.state=None
    def run(self):
        self.p=Popen([self.cmd],*self.popenargs,**self.popenkwargs)
        while self.p.poll() is None:
            # is running, not done
            startit=True
            for check in self.conditions:
                if check():
                    self.p.send_signal(SIGSTOP)
                    self.state=self.STOPPED
                    startit=False
            if startit:
                self.p.send_signal(SIGCONT)
                self.state=self.STARTED
            sleep(self.polltime)

def get_cpu_stats():
    field_names=[ 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice' ]
    with open("/proc/stat") as f:
        data=f.read()
    lines=data.split("\n")
    for line in lines:
        if line[:4] == "cpu ":
            cpustat_line=line[4:].strip()
            break
    cpustat_fields=cpustat_line.split(" ")
    cpustats={}
    for name,field in zip(field_names,cpustat_fields):
        cpustats.update({name:int(field)})

    _sum=sum(cpustats.values())
    for k,v in cpustats.items():
        cpustats.update({k:v/_sum})
    cpustats.update({'sum':_sum})
    return cpustats

def get_iowait():
    return get_cpu_stats()['iowait']

def gen_max_iowait_checker(max_factor):
    def max_iowait_checker():
        if get_iowait() <= max_factor:
                return False
        else:
                return True
    return max_iowait_checker

