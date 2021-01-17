import syslog
from sys import stderr

ERR   =  syslog.LOG_ERR
WARN  =  syslog.LOG_WARNING
INFO  =  syslog.LOG_INFO
DEBUG =  syslog.LOG_DEBUG


def log(msg,level=syslog.LOG_INFO, facility=syslog.LOG_USER, end="",log2stderr=False):
    end="" if end=="\n" else end
    if not type(msg) is str:
        msg=str(msg)
    syslog.syslog(level|facility,msg+end)
    if log2stderr:
        print(msg+end,file=stderr)

def info(msg,log2stderr=False):
    log(msg,level=INFO,log2stderr=log2stderr)
def warn(msg,log2stderr=False):
    log(msg,level=WARN,log2stderr=log2stderr)
def err(msg,log2stderr=False):
    log(msg,level=ERR,log2stderr=log2stderr)
def debug(msg,log2stderr=False):
    log(msg,level=DEBUG,log2stderr=log2stderr)

def log_exp(level,e,with_traceback=True,log2stderr=False):
    from traceback import format_tb
    if with_traceback:
        for line in format_tb(e.__traceback__):
            log(line,level=level)
    log("EXCEPTION("+type(e).__name__+"): "+str(e),level=level,log2stderr=log2stderr)

def warn_exp(e,with_traceback=True,log2stderr=False):
    log_exp(WARN,e,with_traceback=with_traceback,log2stderr=log2stderr)

def format_exp(e,with_traceback=True):
    txt=''
    from traceback import format_tb
    if with_traceback:
        for line in format_tb(e.__traceback__):
            txt+=line+"\n"
    txt+="EXCEPTION("+type(e).__name__+"): "+str(e)
    return txt
