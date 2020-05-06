# coding: utf-8

def print_printbuffer(edit_buffer,col,cols,nr_stay=1):
    from pylib.du import dd,d0,d1
    ret=edit_buffer
    if len(edit_buffer) > nr_stay:
        if nr_stay>0:
            printbuffer=edit_buffer[: - nr_stay]
            ret=edit_buffer[-nr_stay:]
        else:
            printbuffer=edit_buffer
            ret=[]
        for i in printbuffer:
            print(i,end="")
            col[0]+=1
            if col[0]%cols==0:
                print()
                col[0]=0
    return ret

def binprint(data,cols='auto',break0a=True,break_befor_text=True,sep="",skip_space_inside_continues_text=True,space_mark_text2non=True):
    """
    Expects data bytes and prints alligned output
    in mixed hex/ascii style.
    If the output uses 2 characters of space on the screen
    it is to be interpreted as hex,
    else it is ascii encoded.
    """
    was_nonprintable=None
    nonprintable=None
    if cols=="auto":
        from os import get_terminal_size
        from math import floor
        cols=floor(get_terminal_size().columns / 2+len(sep))
    col = [0]
    hexformat="{:02x}"+sep
    strformat="{:>2s}"+sep
    printbuffer=[]
    for i in data:
        breakline = False
        hexprint=False
        if not i in range( 0 , 0x21 ):
            if not i >= 0x7f:
                pass
        else:
            hexprint=True
        if not hexprint:
            try:
                s=strformat.format(bytes([i]).decode())
                if was_nonprintable and break_befor_text:
                    printbuffer.append("\n")
                if not was_nonprintable and skip_space_inside_continues_text:
                    s=s.lstrip(" ")
                printbuffer.append(s)
                nonprintable=False
            except UnicodeError:
                hexprint=True
        if hexprint:
            if not was_nonprintable and space_mark_text2non and skip_space_inside_continues_text and len(printbuffer) > 0:
                printbuffer.append(" ")
                #printbuffer.append("DEBUG "+str(printbuffer[-3:]))
            #if not i in [0x20,0x0a,0x0d]:
            nonprintable = True
            printbuffer.append(hexformat.format(i))
        if break0a and i==0x0a:
            printbuffer.append("\n")
        printbuffer=print_printbuffer(printbuffer,col,cols)
        was_nonprintable=nonprintable
    print_printbuffer(printbuffer,col,cols,nr_stay=0)

def genbytes(r0,l0,r1,l1):
    from random import choice
    def _genbytes(s,r,l):
        bts=[]
        for i in range(1,l+1):
            try:
                b=choice(range(s,r+1))
            except IndexError:
                from pylib.du import dd
                dd(i)
                dd(l)
                dd(s)
                dd(r)
                raise
            bts.append(b)
        return(bytes(bts))
    bts=[]
    for i in range(l1):
        s=choice(range(1,r0))
        r=choice(range(s,r0))
        l=choice(range(1,l0))
        bts+=(_genbytes(s,r,l))
    return bts

def test(gen=False):
    if gen:
        global data
        data=genbytes(255,20,10,10)
    binprint(data)

if __name__ == "__main__":
    test(gen=True)
