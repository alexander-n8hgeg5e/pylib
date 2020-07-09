from os.path import sep as psep,isdir,abspath
from sys import stdout
from os import listdir
from os import walk
from re import match

def looks_git(d,effort="low"):
    """
    tells if the dir "d" looks like a git dir.
    """
    if not effort=="low":
        raise Exception("Other effort stages than low are not implemented yet.")
    if d[-4:]==".git":
        obj_path = d+psep+"objects"
        if isdir(obj_path):
            # means is a dir or a valid link to a dir
            return True
    return False

def are_gitdirs_inside(path,verbose=False,msg_out=stdout,effort="low"):
    """
    Check if this dir contains git dirs or is itself a gitdir
    returns a tuple of len 2
    gitdirs,subdirs that need to be checked
    """
    path=abspath(path)
    if verbose:
        print("checking for git dirs: {}".format(path),file=msg_out)
    if looks_git(path,effort=effort):
        return [path],[]
    dirlist = listdir(path)
    prob_git_dirs = []
    other_subdirs = []
    for d in dirlist:
        fullp=path+psep+d
        if looks_git(fullp,effort=effort):
            prob_git_dirs.append(fullp)
        elif isdir(fullp):
            other_subdirs.append(fullp)
    return prob_git_dirs,other_subdirs

def find_git_dirs(path,effort="low",verbose=False,msg_out=stdout):
    """
    search recursivly for dirs that look like git dirs.
    """
    prob_git_dirs,dirs2check=are_gitdirs_inside(path,effort=effort,verbose=verbose,msg_out=msg_out)
    while len(dirs2check) > 0:
        d=dirs2check.pop()
        a,b=are_gitdirs_inside(d,effort=effort,verbose=verbose)
        prob_git_dirs+=a
        dirs2check+=b
    return prob_git_dirs

def get_git_objects_pathes(git_dir):
    gd=git_dir
    objects=[]
    obj_dir=gd+psep+"objects"
    dirlist=listdir(obj_dir)
    for d in dirlist:
        if len(d) == 2 :
            objects.append(obj_dir+psep+d)
    return objects

def find_git_pack_pathes(git_dir):
    gd=git_dir
    packs=[]
    tree=walk(gd)
    for t in tree:
        dirpath=t[0]
        filenames=t[2]
        for fn in filenames:
            if fn[-5:]==".pack":
                if fn[:5]=="pack-":
                    if match("^[a-fA-F0-9]{20,80}$",fn[5:-5]):
                        packs.append(dirpath+psep+fn)
    return packs
# vim: foldlevel=0 foldnestmax=3 foldmetod=syntax :
