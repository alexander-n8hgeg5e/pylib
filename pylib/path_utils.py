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

def shorten_uniq(f,l=8,uniq_file_ids={}):
    #print(f"\"{f}\" : ",end="")
    if f in uniq_file_ids.keys():
        #print(f"\"{uniq_file_ids[f]}\"")
        return uniq_file_ids[f]
    if len(f) > l:
        sf=f[-l:]
        loopcount=0
        while sf in uniq_file_ids.values() and l > loopcount:
            loopcount+=1
            sf = sha1(f.encode()).hexdigest()[:loopcount] + f[ -l+loopcount:]
        if sf in uniq_file_ids.values():
            raise Exception(f"Could not find uniq file id for file :\n{f}")
    else:
        sf=f
    uniq_file_ids.update({f:sf})
    #print(f"\"{sf}\"")
    return sf
