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
