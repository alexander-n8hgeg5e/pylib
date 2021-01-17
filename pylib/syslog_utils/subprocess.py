DEFAULT_MAXLEN=90

from subprocess import check_output,check_call,DEVNULL,call,Popen,CalledProcessError
for thing in [ 'call','check_call','Popen', 'check_output' ]:
    exec( "from subprocess import " + thing + " as subprocess_" + thing )

from pylib.syslog_utils import warn,err,info,log,WARN,ERR,INFO

from os import get_terminal_size,isatty


def _get_msg0_(*z,shorten_msg='tw',verbose=True,msg=None,result='unknown result',msgprefix="",**zz):
    if not verbose:
        return
    if msg is None:
        msg = "CMD "+result+": "+str(z)
    head=msgprefix+" "
    if shorten_msg=='tw':
        if isatty(1):
            maxlen=get_terminal_size().columns - len(head)
        else:
            maxlen=DEFAULT_MAXLEN-len(head)
        if len(msg) > maxlen:
            msg=msg[:maxlen]
    return head+msg

def call(*z,shorten_msg='tw',verbose=True,msg=None,stdout=DEVNULL,stderr=DEVNULL,loglevel=INFO,log2stderr=False,**zz):
    retval=subprocess_call(*z,stdout=stdout,stderr=stderr,**zz)
    if verbose:
        result=("SUCCESS" if retval==0 else "FAILED")
        msg=_get_msg0_(*z,msg=msg,verbose=verbose,result=result,**zz) 
        log( msg , level=loglevel,log2stderr=log2stderr)
    return(retval)

def check_func(*z,func=None,verbose=True,shorten_msg="tw",stdout="not allowed",loglevel=INFO,msg=None,log2stderr=False,**zz):
    if verbose:
        exc=None
        try:
            retval=func(*z,**zz)
            result="SUCCESS"
        except Exception as e:
            result="FAILED"
            exc=e
        msg=_get_msg0_(*z,msg=msg,verbose=verbose,result=result,**zz) 
        log( msg , level=loglevel,log2stderr=log2stderr)
        if not exc is None:
            raise exc
    return retval

def check_call(*z,**zz):
    return check_func(*z,func=subprocess_check_call,**zz)

def check_output(*z,**zz):
    return check_func(*z,func=subprocess_check_output,**zz)

class Popen(subprocess_Popen):
    def __init__(self,*z,stdout=DEVNULL,stderr=DEVNULL,verbose=True,loglevel=INFO,msg=None,log2stderr=False,**zz):
        if verbose:
            log(_get_msg0_(msg=("BGRND: "+str(z)) if msg is None else msg,verbose=verbose,result="",log2stderr=stderr),level=INFO)
        super().__init__(*z,stdout=stdout,stderr=stderr,**zz)
