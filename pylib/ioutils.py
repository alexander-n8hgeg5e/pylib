from os import set_blocking

class AsyncLineReader():
    def __init__(self,filehandle):
        self.file=filehandle
        set_blocking(filehandle.raw.fileno(),False)
        self.databuffer=b''
        self.linebuffer=[]
    
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
