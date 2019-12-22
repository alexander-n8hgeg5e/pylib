# coding: utf-8
from psutil import pids as get_pids
from warnings import warn
from os import stat
from pwd import getpwuid
from time import sleep
debug=True

class Proc_stat_getter():
    struct_proc_pid_stat=\
    [
    "pid",     "comm",     "state",     "ppid",     "pgrp",     "session",
    "tty_nr",     "tpgid",     "flags",     "minflt",     "cminflt",     "majflt",
    "cmajflt",     "utime",     "stime",     "cutime",     "cstime",     "priority",
    "nice",     "num_threads",     "itrealvalue",     "starttime",     "vsize",
    "rss",     "rsslim",     "startcode",     "endcode",     "startstack",
    "kstkesp",     "kstkeip",     "signal",     "blocked",     "sigignore",
    "sigcatch",     "wchan",     "nswap",     "cnswap",     "exit_signal",
    "processor",     "rt_priority",     "policy",     "delayacct_blkio_ticks",
    "guest_time",     "cguest_time",     "start_data",     "end_data",     "start_brk",
    "arg_start",     "arg_end",     "env_start",     "env_end",     "exit_code", 
    ]
    def _get_stat(self,num,single_pid=None):
        """
        Returns sorted list with pid,stat,percent.
        Higher resource utilization ones first.
        """
        if single_pid is None:
            pids=get_pids()
        else:
            pids=[single_pid]
        stats=[]
        for pid in pids:
            try:
                with open('/proc/'+str(pid)+'/stat') as f:
                    _stats=int(f.read().split()[num])
                    stats.append((pid,_stats))
            except FileNotFoundError as e:
                warn(str(e))
        
        stats.sort(key=lambda x: x[1],reverse=True)
        
        try:
            while stats[-1][1]==0:
                stats.pop()
        except IndexError as e:
            warn(str(e))
        
        s=sum(x[1] for x in stats)
        
        for i in range(len(stats)):
            pid,v = stats[i]
            stats[i]=pid,v,v/s

        return stats
    
    def get_stats(self,*nums_or_names,single_pid=False):
        numlist=[]
        stats={}
        for thing in nums_or_names:
            if type(thing) is str and thing in self.struct_proc_pid_stat:
                numlist.append(self.struct_proc_pid_stat.index(thing))
            elif hasattr(thing,'__int__') and int(thing) < len(self.struct_proc_pid_stat):
                numlist.append(int(thing))
            else:
                raise Exception (
                                    "Error: could not infer a stat from the supplied value.\n"
                                    "    value="+str(thing)+"\n"
                                    "    all args: "+str(nums_or_names)+"\n"
                                )
        for num in numlist:
            name=self.struct_proc_pid_stat[num]
            stats.update({name:self._get_stat(num,single_pid=single_pid)})

        return stats

def gen_max_iowait_checker(max_factor):
    """
    ret True if limit reached
    """
    from psutil import cpu_times_percent
    def get_iowait():
        return cpu_times_percent().iowait
    def max_iowait_checker():
        if debug:
            print("iowait checker is checking iowait...",end="")
        iowait=get_iowait()
        if debug:
            print("val="+str(iowait))
        if iowait <= max_factor:
                return False
        else:
                return True
    return max_iowait_checker

class Pid_throttler():
    tr_methods=['renice','stop','ionice']
    tr_levels=['zero','low','medium','high','full']

    def __init__(self):
        self.pids=[]
        self.pid_data={}
        self.psg=Proc_stat_getter()

    def throttle(self,level):
        for pid in self.pids:
            self._throttle_pid(pid)

    def add_pid(self,pid,methods=['stop','renice'],limits={'maxnice': 19}):
        self.pids.append(pid)
        pid_data={}
        pid_d
        self.pid_data.update(   {
                                 str(pid) : {
                                            'methods': methods ,
                                            'limits':limits,
                                            }
                                },
                            )

    def _backup_pid_data(self,pid):
        stats=self.psg.get_stats('niceness','state',single_pid=pid)
        niceness=stats['niceness'][0][1]
        state=stats['state'][0][1]
        running_state = True if not state in "SsZz" else False
        
        self.pid_data[pid].update   (
                                    {
                                        'backup':
                                                    {
                                                        'niceness':niceness,
                                                        'running':running_state,
                                                    },
                                    },
                                    )

    def _throttle_pid(self,pid):
        if not 'backup' in self.pid_data[str(pid)].keys():
            self._backup_pid_data(str(pid))
        for m in self.tr_methods:
            if m in self.pid_data[str(pid)]['methods']:
                getattr(self,"tr_method_"+m)(level,pid)

    def tr_method_renice(self,level,pid):
        limits={'max':19, 'min': -19}
        limits.update(self.pid_data[str(pid)]['limits'])
        print("tr_renice",level,limits,pid)
        
    def tr_method_stop(self,level,pid):
        print("tr_stop",level,limits,pid)

    def tr_method_ionice(self,level,pid):
        print("tr_stop",level,limits,pid)

class IO_wait_controller():
    exclude_uids=[]
    exclude_stats={}
    limit_stats={}
    limit_uid={}
    method_restrict_stats={}
    method_restrict_uid={}

    sleeptime=5

    def __init__(self,max_iowait=2):
        self.iowait_checker=gen_max_iowait_checker(max_iowait)
        self.pthr=Pid_throttler()
        self.throtte_range=range(10)
        self.thr_level=self.pthr.tr_levels.index("zero")
        self.psg=Proc_stat_getter()

    def _get_uid(pid):
        return stat('/proc/'+str(pid)).st_uid

    def _add_exclude_stat(name,value_or_value_regex):
        ex={self.struct_proc_pid_stat.index(name) : value_or_value_regex}
        self.exclude_stats.update(ex)

    def _add_exclude_user(uid_or_name):
        if type(uid_or_name) is str:
            uid=getpwnam(uid_or_name).pw_uid
        elif hasattr(uid_or_name,'__int__'):
            uid=uid_or_name
        self.exclude_uids.append(uid)

    def get_pid_user_list(self,pids):
        l=[]
        for pid in pids:
            l.append((pid,self._get_uid(pid)))
        return l
    def _check_pid(self,pid):
        """
        return dict with,
        {'exclude':Bool ,'limits':dict ,'methods':list}

        """
        limits={}
        methods=self.pthr.tr_methods
        exclude=False
        if self._get_uid(pid) in self.exclude_uids:
            exclude=True
        keys=list(self.exclude_stats.keys())
        stats=self.psg.get_stats(*keys,single_pid=pid)
        for k,v in stats.items():
            for _pid,_v in v:
                if _pid == pid:
                    if _v == self.exclude_stats[k]:
                        exclude=True
                        # this pid is fully excluded
                        break

                    # if _statval matches requested2limit val
                    if _v == self.limit_stats[k]['val']:
                        limits.update(self.limit_stats[k]['limits'])

                    # if _statval matches requested2restrict method val
                    if _v == self.method_restrict_stats[k]['val']:
                        methods.update(self.method_restrict_stats[k]['methods'])
        return {'exclude':exclude,'methods':methods,'limits':limits}
                    

        
    def run(self):
        while True:
            if self.iowait_checker():
                data={}
                data.update(self.psg.get_stats("delayacct_blkio_ticks"))
                for i in self.throtte_range:
                    check_data=self._check_pid(pid)
                    if not checkdata['exclude']:
                        m=check_data['methods']
                        limits=check_data['limits']
                        self.pthr.add(pid,methods=m,limits=limits)
                self.thr_level+=1
            else:
                self.thr_level-=1

            self.pthr.throttle(self.thr_level)
            sleep(self.sleeptime)

                            
# vim: set foldlevel=0 foldmethod=indent :
