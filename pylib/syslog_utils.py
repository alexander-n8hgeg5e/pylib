import syslog
log_facility = syslog.LOG_USER
INFO=log_facility+syslog.LOG_INFO
WARN=log_facility+syslog.LOG_WARNING
ERR=log_facility+syslog.LOG_ERR
DEBUG=log_facility+syslog.LOG_DEBUG

def info(msg):
    syslog.syslog(INFO,msg)
def warn(msg):
    syslog.syslog(WARN,msg)
def err(msg):
    syslog.syslog(ERR,msg)
def debug(msg):
    syslog.syslog(DEBUG,msg)
def log(msg,level=INFO,end=""):
    end="" if end=="\n" else end
    syslog.syslog(level,msg+end)

def log_exp(level,e,with_traceback=True):
    from traceback import format_tb
    if with_traceback:
        for line in format_tb(e.__traceback__):
            warn(line)
    warn("EXCEPTION: "+str(e))

def warn_exp(e,with_traceback=False):
    log_exp(WARN,e,with_traceback=with_traceback)


from subprocess import check_output,check_call,DEVNULL,call,Popen,CalledProcessError

for thing in [ 'call','check_call','Popen', 'check_output' ]:
    exec( "from subprocess import " + thing + " as subprocess_" + thing )

from pylib.decorators import VerbosityDecorator
from pylib.decorators import Subprocess_Popen_init_VerbosityDecorator
from pylib.decorators import Subprocess_check_call_VerbosityDecorator
from pylib.decorators import Subprocess_call_VerbosityDecorator
from pylib.decorators import Subprocess_check_output_VerbosityDecorator

@Subprocess_check_call_VerbosityDecorator
def check_call(*z,**zz):
        return subprocess_check_call(*z,**zz)

@Subprocess_check_output_VerbosityDecorator
def check_output(*z,**zz):
    return subprocess_check_output(*z,**zz)

@Subprocess_call_VerbosityDecorator
def call(*z,**zz):
        return subprocess_call(*z,**zz)

class Popen(subprocess_Popen):
    def __init__(self,*z,**zz):
        dec = Subprocess_Popen_init_VerbosityDecorator(super().__init__)
        dec.__call__(*z,**zz)
    
