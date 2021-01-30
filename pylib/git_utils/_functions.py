from os.path import sep as psep,isdir,abspath
from sys import stdout
from os import listdir
from os import walk
from re import match
from os import makedirs
from subprocess import check_output
from sys import argv,exit
from sys import stdout
from os.path import dirname
from os.path import sep as psep,pardir,normpath,exists
from os import rename,listdir
from os.path import basename,abspath
from subprocess import Popen,PIPE,DEVNULL
from .constants import UNPACK_PACKS_EXTRA_DIR_NAME as EXTRA_DIR_NAME
from .constants import MAX_HASH_LEN

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
    todo=[]
    obj_dir=gd+psep+"objects"
    dirlist=listdir(obj_dir)
    for d in dirlist:
        if len(d) == 2 :
            todo.append(obj_dir+psep+d)
    objects=[]
    for p in todo:
        for w in walk(p):
            w0=w[0]
            w2=w[2]
            for f in w2:
                objects.append(w0+psep+f)
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

def unpack_packs(gitdirs,verbose=False):
    for gitdir in gitdirs:
        if verbose:
            print(" processing gitdir: {}".format(gitdir))
        # check if everything as expected
        if abspath(gitdir) != gitdir:
            raise Exception("not as programmer expected, need check")

        # create extra dir for the packs
        extra_dir=gitdir+psep+EXTRA_DIR_NAME
        proper_pack_dir=gitdir+psep+"objects"+psep+"pack"
        makedirs(extra_dir,exist_ok=True)
        packs=find_git_pack_pathes(gitdir)

        # mv only packs from the proper pack dir
        packs_ok=[]
        packs_not_ok=[]
        for pack in packs:
            if abspath(pack)!=pack:
                raise Exception("not as programmer expected, need check")
            if proper_pack_dir+psep+basename(pack)==pack:
                packs_ok.append(pack)
            else:
                packs_not_ok.append(pack)
        packs=packs_ok

        # now got ok packs that are inside gitdir/packs
        for pack in packs:
            pack_bn = basename(pack)
            new_pack_path     = extra_dir+psep+pack_bn
            rename(pack, new_pack_path)

            # also move the pack's index file
            idx = pack[:-4]+"idx"
            if exists(idx):
                idx_bn  = basename(idx)
                new_idx_path = extra_dir+psep+idx_bn
                rename(idx , new_idx_path)

        # not ok packs are packs that are most likely
        # already inside the "extra-dir"
        # check if the corresponding idx file also was moved,
        # so no orphan idx files will remain inside the pack dir
        for pack in packs_not_ok:
            pack_bn = basename(pack)
            if not pack == extra_dir+psep+pack_bn:
                # only move the ones that are inside the extra dir
                continue
            idx_bn  = pack_bn[:-4]+"idx"
            idx  = proper_pack_dir+psep+idx_bn
            idx_new =  extra_dir+psep+idx_bn
            if exists(idx):
                # move it
                rename(idx,idx_new)

        #-------------#
        #  unpacking  #
        #-------------#
        # check if pack dir is empty(no packs)
        ok=True
        dirlist = listdir(proper_pack_dir)
        for d in dirlist:
            if d[-5:]==".pack":
                ok=False
                break
        if not ok:
            raise Exception("""ERROR: expected no packs inside the pack dir.
            Could not move the packs or something other went wrong.""")


        # get pack list
        packs2unpack=[]
        dirlist = listdir(extra_dir)
        for p in dirlist:
            if p[-5:]==".pack":
                packs2unpack.append(extra_dir+psep+p)

        # Now read the pack data and
        # and feed it into the "git unpack-objects" cmd.
        for pack in packs2unpack:
            with open(pack,mode="rb") as f:
                data=f.read()
            cmd=['git','--git-dir='+gitdir,'unpack-objects']
            if not verbose:
                cmd.append('-q')
            p=Popen(cmd,stdin=PIPE)
            p.stdin.write(data)
            p.wait()

        # move the packs back
        # I ran git gc and
        # git removed the redundant packs.
        # Because git knows what is does,
        # git is the right program for the task.
        for pack in packs2unpack:
            idx  = pack[:-4]+"idx"
            pack_bn = basename(pack)
            idx_bn  = basename(idx)
            idx_new  = proper_pack_dir+psep+idx_bn
            pack_new = proper_pack_dir+psep+pack_bn
            rename(pack, pack_new)
            rename(idx,  idx_new)

def get_hash_from_obj_path(p):
    h=[]
    i=0
    j=0
    while j < MAX_HASH_LEN:
        i+=1
        c=p[-i]
        if c!=psep:
            if c!="s":
                h.append(c)
                j+=1
            else:
                break
    h.reverse()
    return "".join(h)


# vim: foldlevel=0 foldnestmax=3 foldmethod=indent :
