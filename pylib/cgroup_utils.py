from subprocess import Popen,PIPE

def cgroup2_find_path():
    shell_code=". /lib/rc/sh/rc-cgroup.sh \n cgroup2_find_path"
    p=Popen(["bash"],stdin=PIPE,stdout=PIPE)
    outp=p.communicate(input=shell_code.encode())
    return outp[0].decode()
    
