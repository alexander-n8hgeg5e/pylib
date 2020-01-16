from pylib.syslog_utils import warn,err,info,log,WARN,ERR,INFO,warn_exp


class XinitError(Exception):
    @staticmethod
    def gen_msg(msg):
        msgline="##  ERROR: "+str(msg)+"  ##"
        headline=(len(msgline)*"#")
        footerline=headline
        return "\n"+headline+"\n"+msgline+"\n"+footerline

    def log(self,with_traceback=True):
        from traceback import format_tb
        tb=format_tb(self.__stacktrace__)
        msg=self.msg + (("\n"+ tb) if with_traceback else "")
        err(gen_msg(msg))

class SkyscraperError(XinitError):
    pass

class SkyscraperNotReadyError(SkyscraperError):
    pass

class SkyscraperNotAwakeError(SkyscraperError):
    def __init__(self,*z,**zz):
        if len(z) == 1:
            super().__init__(self.gen_msg(z[0]), **zz)
        elif len(z) > 1:
            super().__init__(self.gen_msg(z[0]), *z[:1] ,**zz)
        else:
            super().__init__(self.gen_msg("skyscraper seems down and could not be awaken"),**zz)
