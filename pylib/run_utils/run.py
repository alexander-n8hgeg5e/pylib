from subprocess import check_call
from pylib.du import dd
from types import FunctionType

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

