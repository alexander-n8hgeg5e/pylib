# coding: utf-8
from psutil import pids as get_pids
from warnings import warn
from os import stat,kill
from pwd import getpwuid
from time import sleep
from math import nan
from pylib.du import ptb
from pylib.random import random_bool_of_num
from fractions import Fraction
from signal import SIGCONT,SIGSTOP
from pprint import pprint
from subprocess import check_call,DEVNULL
from sys import stderr

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
        #        
        for pid in pids:
            try:
                with open('/proc/'+str(pid)+'/stat') as f:
                    _stats=f.read().split()[num]
                    if hasattr(_stats,'__int__'):
                        _stats=int(_stats)
                    stats.append((pid,_stats))
            except FileNotFoundError as e:
                warn(str(e))
        
        stats.sort(key=lambda x: x[1],reverse=True)
        
        try:
            while stats[-1][1]==0:
                stats.pop()
        except IndexError as e:
            warn(str(e))
        
        s=sum((x[1] if hasattr(x[1],'__int__') else nan ) for x in stats)
        
        for i in range(len(stats)):
            pid,v = stats[i]
            stats[i]=pid,v,(v if hasattr(v,'__int__') else nan)/s

        return stats
    
    def get_stats(self,*nums_or_names,single_pid=None):
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

def gen_max_iowait_checker(max_factor,debug=False,verbose=True):
    """
    ret True if limit reached
    """
    from psutil import cpu_times_percent
    def get_iowait():
        return cpu_times_percent().iowait
    def max_iowait_checker():
        if debug:
            print("iowait checker is checking iowait...",end="",file=stderr)
        iowait=get_iowait()
        if debug or verbose:
            print("val="+str(iowait),file=stderr)
        if iowait <= max_factor:
                if debug:
                    print("iowait ok")
                return False
        else:
                if debug:
                    print("iowait high")
                return True
    return max_iowait_checker

class Pid_throttler():
    """
    """
    #tr_methods=['renice','stop','ionice']
    tr_methods=['stop']
    tr_levels=['zero','low','medium','high','full']

    number_levels=10

    def __init__(self,debug=False,verbose=False):
        self.pids=[]
        self.pid_data={}
        self.psg=Proc_stat_getter()
        self.need_restore_sigcont=[]
        self.need_restore_sigcont_cmds=[]
        self.need_restore_sigcont_cmds_sudo=[]
        self.debug=debug
        self.verbose=verbose if not debug else True

    def throttle(self,level,pretend=True):
        """
        The level is 0 for no throttle.
        The level for max throttle is
        Pid_throttler.number_levels - 1 .
        """
        for pid in self.pids:
            if self.debug:
                print('applying level "'+str(level)+'"')
            self._throttle_pid(pid,level,pretend=pretend)

    def add_pid(self,pid,methods=['stop','renice'],limits={'maxnice': 19}):
        if not pid in self.pids:
            self.pids.append(pid)
            pid_data={}
            self.pid_data.update(   {
                                    str(pid) : {
                                                    'methods': methods ,
                                                    'limits':limits,
                                                }
                                    },
                                )
        if self.debug:
            print("added pid: "+str(pid))

    def remove_pid(self,pid):
        self.pids.pop(str(pid))
        self.pid_data.pop(str(pid))
        if self.debug:
            print("removed pid: "+str(pid))

    def _backup_pid_data(self,pid):
        stats=self.psg.get_stats('nice','state',single_pid=pid)
        niceness=stats['nice'][0][1]
        state=stats['state'][0][1]
        
        self.pid_data[pid].update   (
                                    {
                                        'backup':
                                                    {
                                                        'niceness':niceness,
                                                        'state':state,
                                                    },
                                    },
                                    )

    def _throttle_pid(self,pid,level,pretend=True):
        if not 'backup' in self.pid_data[str(pid)].keys():
            self._backup_pid_data(str(pid))
        if self.debug:
            print("throttle methods=",self.tr_methods)
        for m in self.tr_methods:
            if m in self.pid_data[str(pid)]['methods']:
                getattr(self,"tr_method_"+m)(level,pid,pretend=pretend)

    def tr_method_renice(self,level,pid,pretend=True):
        limits={'max':19, 'min': -19}
        limits.update(self.pid_data[str(pid)]['limits'])
        
    def tr_method_stop(self,level,pid,pretend=True):
        if self.verbose:
            print("level="+str(level))
        try:
            if random_bool_of_num(level,self.number_levels):
                if pretend:
                    print("would send SIGSTOP to pid",pid,file=stderr)
                    print(file=stderr)
                else:
                    self._stop_pid(pid)
            else:
                if pretend:
                    print("would send SIGCONT to pid:",pid,file=stderr)
                    print(file=stderr)
                else:
                    try:
                        if self.debug or self.verbose:
                            print("SIGCONT->"+str(pid))
                        kill(pid,SIGCONT)
                    except Exception as e:
                        ptb(e)
        except ProcessLookupError:
            if self.debug:
                print("pid not found, removing pid: "+str(pid),file=stderr)
            self.remove_pid(pid)
    
        # def gs(stat):
        #     s=self.controller.psg.get_stats(stat,single_pid=pid)[stat]
        #     return str(s[0][1])
        # print("tr_stop level="+str(level)+" pid="+ str(pid)+" cmd="+str(gs('comm')))

    def _stop_pid(self,pid):
        try:
            check_call(['kill','-V'],stderr=DEVNULL,stdout=DEVNULL)
            cmd=['kill','-sSIGCONT',str(pid)]
            sudocmd=['sudo']+cmd

            if pid not in self.need_restore_sigcont:
                a=True
            if cmd not in self.need_restore_sigcont_cmds:
                b=True
            if sudocmd not in self.need_restore_sigcont_cmds_sudo:
                c=True

            with open('/proc/'+str(pid)+'/stat','rb',buffering=0) as f:
                data=b''
                while True:
                    data+=f.read(10)
                    fields=data.split(b" ")
                    if len(fields) >= 4:
                        break
                if not fields[2] in b'TZX':
                    if self.debug or self.verbose:
                        print("sending SIGSTOP to "+str(pid))
                    kill(pid,SIGSTOP)
                    self.need_restore_sigcont.append(pid)
                    self.need_restore_sigcont_cmds.append(cmd)
                    self.need_restore_sigcont_cmds_sudo.append(sudocmd)
        except Exception as e:
            ptb(e)
        
    def tr_method_ionice(self,level,pid,pretend=True):
        pass
        # def gs(stat):
        #     s=self.controller.psg.get_stats(stat,single_pid=pid)[stat]
        #     return str(s[0][1])
        # print("tr_ionice level="+str(level)+" pid="+ str(pid)+" cmd="+str(gs('comm')))

    def _cleanup(self):
        try:
            for pid in self.need_restore_sigcont:
                try:
                    kill(pid,SIGCONT)
                except Exception as e:
                    ptb(e)
        except Exception as e:
            ptb(e)
            try:
                for cmd in self.need_restore_sigcont_cmds:
                    try:
                        check_call(cmd)
                    except Exception as e:
                        ptb(e)
            except Exception as e:
                ptb(e)
                try:
                    for sudocmd in self.need_restore_sigcont_cmds_sudo:
                        try:
                            check_call(sudocmd)
                        except Exception as e:
                            ptb(e)
                except Exception as e:
                    ptb(e)

    def __del__(self):
        self._cleanup()

class IO_wait_controller():
    exclude_stats=  {
                    'uid' :
                            [
                            0,
                            1000,
                            ],
                    }
    limit_stats={'uid':{'limits':{},"vals":[]}}
    method_restrict_stats={'uid':{'methods':{},'vals':[]},'delayacct_blkio_ticks':{'methods':{},'vals':[]}}

    sleeptime=5

    def __init__(self,max_iowait=2):
        self.iowait_checker=gen_max_iowait_checker(max_iowait)
        self.pthr=Pid_throttler()
        self.throtte_range=10
        self.thr_level=self.pthr.tr_levels.index("zero")
        self.psg=Proc_stat_getter()
        self._gen_stat_keys()

    def _get_uid(self,pid):
        return stat('/proc/'+str(pid)).st_uid

    def _add_exclude_stat(self,name,value_or_value_regex):
        ex={self.struct_proc_pid_stat.index(name) : value_or_value_regex}
        self.exclude_stats.update(ex)

    def _add_exclude_user(self,uid_or_name):
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

    def _gen_stat_keys(self):
        sls=self.limit_stats
        ses=self.exclude_stats
        smrs=self.method_restrict_stats
        _keys=list(sls)
        _keys+=list(ses)
        _keys+=list(smrs)
        keys=[]
        for k in _keys:
            if not k in keys:
                keys.append(k)
        self.stat_keys=keys
        keys_psg=keys.copy()
        keys_psg.remove('uid')
        self.stat_keys_psg=keys_psg

    def _get_stats_single_pid(self,pid):
        stats=self.psg.get_stats(*self.stat_keys_psg,single_pid=pid)
        stats.update({'uid':[(pid,self._get_uid(pid),None)]})
        return stats

    def _check_pid(self,pid):
        """
        return dict with,
        {'exclude':Bool ,'limits':dict ,'methods':list}

        """
        limits={}
        methods=self.pthr.tr_methods
        exclude=False
        stats=self._get_stats_single_pid(pid) 
        sls=self.limit_stats
        ses=self.exclude_stats
        smrs=self.method_restrict_stats
        for k,v in stats.items():
            #            
            #            
            for _pid,_v,_vp in v:
                if _pid == pid:
                    if k in ses and _v in self.exclude_stats[k]:
                        exclude=True
                        # this pid is fully excluded
                        break

                    # if _statval matches requested2limit val
                    if k in sls and _v in self.limit_stats[k]['vals']:
                        limits.update(self.limit_stats[k]['limits'])

                    # if _statval matches requested2restrict method val
                    if k in smrs and _v in self.method_restrict_stats[k]['vals']:
                        methods.update(self.method_restrict_stats[k]['methods'])
        return {'exclude':exclude,'methods':methods,'limits':limits}
    
    def _check_add(self,pid):
        check_data=self._check_pid(pid)
        if not check_data['exclude']:
            m=check_data['methods']
            limits=check_data['limits']
            self.pthr.add_pid(pid,methods=m,limits=limits)
        elif debug:
            excluding_pid=str(pid)
            dd(excluding_pid)
            uid=str(self._get_uid(pid))

    def run(self,pretend=True):
        try:
            while True:
                if self.iowait_checker():
                    self.thr_level+=1

                    data=self.psg.get_stats("delayacct_blkio_ticks")
                    data.update(self.psg.get_stats("state"))

                    if debug:
                        data_debug=self.psg.get_stats("comm")

                    #for i in range(min(self.throtte_range,len(data["delayacct_blkio_ticks"]))):
                    #    pid=data['delayacct_blkio_ticks'][i][0]
                    #    self._check_add(pid)
                    for s in data['state']:
                        if s[1]in "DT":
                            self._check_add(s[0])

                else:
                    self.thr_level-=1
                self.thr_level=min(max(0,self.thr_level),4)
                self.pthr.controller=self
                self.pthr.throttle(self.thr_level,pretend=pretend)
                sleep(self.sleeptime)
        except Exception as e:
            ptb(e)
            self.pthr.__del__()


                            
# vim: set foldlevel=1 foldmethod=indent foldnestmax=2 :
