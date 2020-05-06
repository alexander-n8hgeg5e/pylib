# coding: utf-8


def binprint(data,cols='auto',break0a=True,break_befor_text=True,sep=" "):
    """
    Expects data bytes and prints alligned output
    in mixed hex/ascii style.
    If the output uses 2 characters of space on the screen
    it is to be interpreted as hex,
    else it is ascii encoded.
    """
    was_nonprintable=False
    if cols=="auto":
        from os import get_terminal_size
        from math import floor
        cols=floor(get_terminal_size().columns / 2+len(sep))
    col = 0
    hexformat="{:02x}"+sep
    strformat="{:>2s}"+sep
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
                    print()
                    col=0
                print(s,end='')
                was_nonprintable=False
            except UnicodeError:
                hexprint=True
    
        if hexprint:
            if not i in [0x20,0x0a,0x0d]:
                was_nonprintable = True
            print(hexformat.format(i),end="")
    
        col+=1
        if col%cols==0:
            breakline=True
        if break0a and i==0x0a:
            breakline=True
        if breakline:
            print()
            col=0
