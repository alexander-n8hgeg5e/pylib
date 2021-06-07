from os.path import abspath,sep as psep,exists
from os import mkdir

def mkdir_recursive(p, mode=511, dir_fd=None):
    p=abspath(p)
    parts = p.strip().strip(psep).split(psep)
    #print(f'parts of path: "{parts}"')
    for i in range(len(parts)):
        #print(f"i={i} parts[i]={parts[i]}")
        want_to_exist = psep+psep.join(parts[0:i+1])
        if not exists(want_to_exist):
            print(f"mkdir \"{want_to_exist}\"")
            mkdir(want_to_exist)
