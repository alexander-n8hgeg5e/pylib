from os import environ

def get_uniq_xdisplay_string():
    d = environ['DISPLAY']
    a,b = d.split(":")
    if a.strip() == "":
        from socket import gethostname
        a=gethostname()

    return a+":"+b
