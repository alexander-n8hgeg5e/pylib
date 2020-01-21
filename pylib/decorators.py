from pylib.du import dd
from sys import stderr,stdout,modules
from os import get_terminal_size
from sys import stderr as sys_stderr,stdout as sys_stdout
from subprocess import CalledProcessError,DEVNULL
from pylib.syslog_utils import warn,err,info,log,WARN,ERR,INFO
    

class SubprocessVerbosityDecorator():
    kwargs= {
                'msg':None,
                'initdec':False,
                'verbose':True,
                'shorten_msg':'tw',
            }
    def __new__(cls,*z,exclude_kwargs=[],**zz):
        log("__new__",cls.__name__)
        d=cls.DecoratorGenerator(*z,exclude_kwargs=exclude_kwargs,**zz)
        c=d.Decorator
        log("__new__",cls.__name__)
        return d.Decorator.__new__(c,*z,**zz)

    class DecoratorGenerator():
        def __new__( cls,*z,exclude_kwargs=[],**zz):
            class Decorator():
                def_zz=None
                def __new__(cls,*z,**zz):
                    log("__new__",cls.__name__)
                def __init__(self,*z,**zz):
                    log( "uisufi" )
            kwargs={}
            for k,v in SubprocessVerbosityDecorator.kwargs.items():
                if not k in exclude_kwargs:
                    kwargs.update({k:v})
            Decorator.def_zz=kwargs
            if not initdec:
                Decorator.__init__=cls.get_init(def_zz=kwargs)
                Decorator.__call__=cls.get_call(def_zz=kwargs)
                return Decorator.__new__(*z,**kwargs)
            return( cls.__new__(cls,*z,**zz) )
        def __init__( self,*z, exclude_kwargs=[],initdec=False ,**zz):
            log("__init__",self.__class__.__name__)
        @classmethod
        def get_init(self,def_zz=None):
            def init(self,f,*z,def_zz=def_zz,**zz):
                self.f=f
                log("##############")
            return init
        @classmethod
        def get_call(cls,def_zz={}):
            log(cls,def_zz)
            call_0=cls.get_call_0(cls,def_zz=def_zz)
            call_1=cls.get_call_1(cls,def_zz=def_zz)
            def call(*z,**zz):
                call_0(*z,**zz)
                return call_1(*z,**zz)
            return call
        @classmethod
        def get_call_0(cls,def_zz={}):
            def call_0(*z,def_zz=def_zz,**zz):
                global stderr
                global stdout
                if not 'stderr' in zz.keys():
                    zz['stderr']=stderr
                if not 'stdout' in zz.keys():
                    zz['stdout']=stdout
                elif self.no_stdout:
                    zz.pop("stdout")
                if def_zz['verbose'] and def_zz['msg'] is None:
                   msg = str(z)
                end=" ... "
                head="CMD: "
                if verbose and shorten_msg=='tw':
                    maxlen=get_terminal_size().columns - len(end) - len(head)
                    if len(msg) > maxlen:
                        msg=msg[:maxlen]
                if verbose:
                    log(head+msg,end=end)
            return call_0

        def get_call_1(cls,def_zz=None):
            def call_1(self,*z,def_zz=def_zz,**zz):
                retval = ""#self.f(*z,**zz)
                if type(retval) is int:
                    if verbose:
                        log( "success" if retval==0 else "failed" )
                    return(retval)
                else:
                    return retval
            return call_1

class VerbosityDecorator():
    msgprefix=""

    def __init__(self,f):
        self.f=f

    def __call__(self,*z,shorten_msg='tw',verbose=True,msg=None,stdout=DEVNULL,stderr=DEVNULL,**zz):
        self._pre_(*z,msg=msg,verbose=verbose,**zz)
        return self._post_(*z,verbose=verbose,stdout=stdout,stderr=stderr,**zz)

    def _pre_(self,*z,shorten_msg='tw',verbose=True,msg=None,**zz):
        if verbose and msg is None:
           msg = "CMD: "+str(z)
        head=self.msgprefix+" "
        end=" ... "
        if verbose and shorten_msg=='tw':
            maxlen=get_terminal_size().columns - len(end) - len(head)
            if len(msg) > maxlen:
                msg=msg[:maxlen]
        if verbose:
            self.verbose_msg= head+msg+end

    def _post_(self,*z,stdout=DEVNULL,stderr=DEVNULL,**zz):
        self.f(*z,stdout=stdout,stderr=stderr,**zz)

class Subprocess_call_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,verbose=True,stdout=DEVNULL,stderr=DEVNULL,**zz):
        retval=self.f(*z,stdout=stdout,stderr=stderr,**zz)
        if verbose:
            msg=self.verbose_msg + ("SUCCESS" if retval==0 else "FAILED")
            log( msg , level=INFO)
        return(retval)

class Subprocess_Popen_init_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,stdout=DEVNULL,stderr=DEVNULL,verbose=True,**zz):
        self.f(*z,stdout=stdout,stderr=stderr,**zz)
        if verbose:
            log( "BGRND: "+ self.verbose_msg ,level=INFO)

class Subprocess_check_output_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,verbose=True,stdout=None,stderr=DEVNULL,**zz):
        if verbose:
            try:
                retval=self.f(*z,stderr=stderr,**zz)
                msg=self.verbose_msg + "SUCCESS"
                log( msg , level=INFO)
                return retval
            except Exception as e:
                msg=self.verbose_msg + "FAILED"
                log( msg , level=INFO)
                raise
        else:
            return self.f(*z,stderr=stderr,**zz)

class Subprocess_check_call_VerbosityDecorator(Subprocess_check_output_VerbosityDecorator):
    pass

# vim: foldmethod=indent foldlevel=0 :
