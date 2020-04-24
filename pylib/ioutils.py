from os import set_blocking

class AsyncLineReader():
    def __init__(self,filehandle):
        self.file=filehandle
        set_blocking(filehandle.raw.fileno(),False)
        self.databuffer=b''
        self.linebuffer=[]

    def read_all(self):
        set_blocking(self.file.raw.fileno(),True)
        return self.read()
    
    def read(self):
        data=self.file.read()
        self.databuffer+=data if not data is None else b''
        lines=self.databuffer.split(b"\n")
        incomplete_tail=lines[-1]
        # check if there was a newline
        if len(lines) > 1 :
            complete_lines=lines[:-1]
            # shorten the data, remove complete lines
            self.databuffer=incomplete_tail
            # add them to linebuffer
            self.linebuffer+=complete_lines
        # save lines to return
        retlines=self.linebuffer
        # delete what will be returned
        self.linebuffer=[]
        return retlines

class AsyncLineReader_v2():
    def __init__(self,filehandle_or_fileno):
        from _io import _IOBase
        if _IOBase.__subclasscheck__(type(filehandle_or_fileno)):
            self.file   = filehandle_or_fileno
            self.fileno = filehandle_or_fileno.raw.fileno()
        elif type(filehandle_or_fileno) is int:
            self.fileno = filehandle_or_fileeno
            self.file   = open(filehandle_or_fileno)
        set_blocking(self.fileno,False)
        self.databuffer=b''
        self.linebuffer=[]


