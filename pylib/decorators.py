from pylib.du import dd
from sys import stderr,stdout,modules
from os import get_terminal_size
from sys import stderr,stdout
from subprocess import CalledProcessError

class SubprocessVerbosityDecorator():
    kwargs= {
                'msg':None,
                'initdec':False,
                'verbose':True,
                'shorten_msg':'tw',
            }
    def __new__(cls,*z,exclude_kwargs=[],**zz):
        print("__new__",cls.__name__)
        d=cls.DecoratorGenerator(*z,exclude_kwargs=exclude_kwargs,**zz)
        c=d.Decorator
        print("__new__",cls.__name__)
        return d.Decorator.__new__(c,*z,**zz)

    class DecoratorGenerator():
        def __new__( cls,*z,exclude_kwargs=[],**zz):
            class Decorator():
                def_zz=None
                def __new__(cls,*z,**zz):
                    print("__new__",cls.__name__)
                def __init__(self,*z,**zz):
                    print( "uisufi" )
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
            print("__init__",self.__class__.__name__)
        @classmethod
        def get_init(self,def_zz=None):
            def init(self,f,*z,def_zz=def_zz,**zz):
                self.f=f
                print("##############")
            return init
        @classmethod
        def get_call(cls,def_zz={}):
            print(cls,def_zz)
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
                    print(head+msg,end=end)
            return call_0

        def get_call_1(cls,def_zz=None):
            def call_1(self,*z,def_zz=def_zz,**zz):
                retval = ""#self.f(*z,**zz)
                if type(retval) is int:
                    if verbose:
                        print( "success" if retval==0 else "failed" )
                    return(retval)
                else:
                    return retval
            return call_1

class VerbosityDecorator():
    msgprefix="CMD:"

    def __init__(self,f):
        self.f=f

    def __call__(self,*z,shorten_msg='tw',verbose=True,msg=None,**zz):
        self._pre_(*z,**zz)
        return self._post_(*z,**zz)

    def _pre_(self,*z,shorten_msg='tw',verbose=True,msg=None,**zz):
        if not 'stderr' in zz.keys():
            zz['stderr']=stderr
        if not 'stdout' in zz.keys():
            zz['stdout']=stdout
        if verbose and msg is None:
           msg = str(z)
        end=" ... "
        head=self.msgprefix+" "
        if verbose and shorten_msg=='tw':
            maxlen=get_terminal_size().columns - len(end) - len(head)
            if len(msg) > maxlen:
                msg=msg[:maxlen]
        if verbose:
            print(head+msg,end=end)

    def _post_(self,*z,**zz):
        self.f(*z,**zz)

class Subprocess_call_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,verbose=True,**zz):
        retval=self.f(*z,**zz)
        if verbose:
            print( "success" if retval==0 else "failed" )
        return(retval)

class Subprocess_Popen_init_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,verbose=True,**zz):
        self.f(*z,**zz)
        if verbose:
            print( "initialized" )

class Subprocess_check_output_VerbosityDecorator(VerbosityDecorator):
    def _post_(self,*z,verbose=True,**zz):
        return self.f(*z,**zz)

class Subprocess_check_call_VerbosityDecorator(Subprocess_check_output_VerbosityDecorator):
    pass
