import syslog
ERR   =  syslog.LOG_ERR
WARN  =  syslog.LOG_WARNING
INFO  =  syslog.LOG_INFO
DEBUG =  syslog.LOG_DEBUG


def log(msg,level=syslog.LOG_INFO, facility=syslog.LOG_USER, end=""):
    end="" if end=="\n" else end
    if not type(msg) is str:
        msg=str(msg)
    syslog.syslog(level|facility,msg+end)

def info(msg):
    log(msg,level=INFO)
def warn(msg):
    log(msg,level=WARN)
def err(msg):
    log(msg,level=ERR)
def debug(msg):
    log(msg,level=DEBUG)

def log_exp(level,e,with_traceback=True):
    from traceback import format_tb
    if with_traceback:
        for line in format_tb(e.__traceback__):
            log(line,level=level)
    log("EXCEPTION("+type(e).__name__+"): "+str(e),level=level)

def warn_exp(e,with_traceback=True):
    log_exp(WARN,e,with_traceback=with_traceback)
