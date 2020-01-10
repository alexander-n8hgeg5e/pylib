from argparse import Action,ArgumentParser,ArgumentDefaultsHelpFormatter
from subprocess import call
from os import get_terminal_size
from re import sub
from pylib.du import dd

def get_default_args(argument_parser,try_filter_unset=False):
    """
    returns a list with option_strings,default
    from a argparse.ArgumentParser
    """
    lines=[]
    for a in argument_parser._actions:
        if len(a.option_strings) > 1:
            o=a.option_strings[0] if (len(a.option_strings[0]) > len(a.option_strings[1])) else a.option_strings[1]
        elif len(a.option_strings) >0 :
            o=a.option_strings[0]
        else:
            o=None
        if try_filter_unset:
            if not a.default==None and not o is None and not o=="--help" \
                    and not (type(argument_parser) is PassThroughArgumentParser \
                    and (   o in argument_parser.default_pass_through_args \
                            or o in argument_parser.default_kw_pass_through_args \
                            or o[0:5]=="--no-" or o[0:2]=="-n")):
                lines.append([o,a.default])
        elif not o is None and not o=="--help":
            lines.append([o,a.default])
    return lines

class Default_help_action(Action):
    default_help=' (default: %(default)s)'
    def __init__(self,*z,help="",default=None,**zz):
        if not default is None:
            help=help+self.default_help
        super().__init__(*z,help=help,**zz)

class Action_add_pass_through_arg(Default_help_action):
    def __init__(self, *z, nargs=0, **zz):
        super().__init__(*z, nargs=nargs, **zz)
    def __call__(self, parser, namespace, values, option_string):
        if self.dest in parser.ignore_destinations:
            return
        for val in values:
            if val in parser.ignore_destinations:
                return
        #dd(self.dest)
        if self.dest == "pass_through_args":
            for v in values:
                if not v in namespace.pass_through_args:
                    #dd(v)
                    # add whatever it is
                    namespace.pass_through_args.append(v)
        else:
            if not any(os in namespace.pass_through_args for os in self.option_strings):
                key="--"+sub('_','-',self.dest)
                namespace.pass_through_args.append(key)
            setattr(namespace,self.dest,True)

class Action_add_kw_pass_through_arg(Default_help_action):
    def __init__(self, *z, nargs=None, **zz):
        super().__init__(*z, nargs=nargs, **zz)
    def __call__(self, parser, namespace, values, option_string):
        #print(self.dest)
        if self.dest in parser.ignore_destinations:
            #dd("return")
            return
        if self.dest == "kw_pass_through_args":
            #print(values)
            for v in values:
                #dd(v)
                if not v in namespace.kw_pass_through_args:
                    # add whatever it is
                    #dd(v)
                    namespace.kw_pass_through_args.update({option_string:v})
        else:
            if not self.const is None:
                val=self.const
            else:
                val=values
            key="--"+sub('_','-',self.dest)
            dd(key)
            namespace.kw_pass_through_args.update({key:val})
            setattr(namespace,self.dest,val)
            #setattr(parser._actions[''],self.dest,val)

class Action_remove_pass_through_arg(Default_help_action):
    def __init__(self,*z,nargs=0,**zz):
        super().__init__(*z,nargs=nargs,**zz)
    def __call__(self, parser, namespace, values, option_string):
        if self.dest in parser.ignore_destinations:
            return
        if self.dest in "pass_through_args":
            # no remove support here
            return
        else:
            for os in self.option_strings:
                osr="-"+os.strip("-n")
                if osr in namespace.pass_through_args:
                    namespace.pass_through_args.remove(osr)
                osr="--" + os.strip("--no-")
                if osr in namespace.pass_through_args:
                    namespace.pass_through_args.remove(osr)
            setattr(namespace,self.dest,False)


def prepare_kw_pass_through_args(kwargs):
    l=[]
    for i,j in kwargs.items():
        if i[-1]=="=":
            l+=["".join((i,j))]
    else:
            l+=[i,j]
    return l

class PassThroughArgumentParser(ArgumentParser):
    def __init__(self, *z, wrapped_cmd=[], default_pass_through_args=[], ignore_destinations=[],default_kw_pass_through_args={}, **zz):
        self.ignore_destinations=ignore_destinations
        self.wrapped_cmd=wrapped_cmd
        self.default_pass_through_args=default_pass_through_args
        self.default_kw_pass_through_args=default_kw_pass_through_args
        super().__init__(
                            *z,
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            **zz,
                        )
        self.add_argument( dest='pass_through_args', nargs="*", action=Action_add_pass_through_arg, default=default_pass_through_args)
        self.add_argument( dest='kw_pass_through_args', nargs="*", action=Action_add_kw_pass_through_arg, default=default_kw_pass_through_args)
        self.add_argument('--debug',"-D",action="store_true",default=False)
        self.add_argument('-v','--verbose',action='store_true',default=False)
        for a in self._actions:
            print(a)

    #def error(self,*msg,**zz):
    #    print(msg,zz)
    #def _get_kwargs(self):
    #    print('hello')
    #    names = [
    #        'prog',
    #        'usage',
    #        'description',
    #        'formatter_class',
    #        'conflict_handler',
    #        'add_help',
    #    ]
    #    return [(name, getattr(self, name)) for name in names]

    def add_argument(self,*z,**zz):
        if 'dest' in zz.keys() and zz['dest'] =='pass_through_args':
            print("add arg pass_through_args")
            print("z,zz:",z,zz)
            for a in self._actions:
                if a.dest=='pass_through_args':
                    print(a)
        super().add_argument(*z,**zz)
        if 'dest' in zz.keys() and zz['dest'] =='pass_through_args':
            print("add arg pass_through_args after super call")
            for a in self._actions:
                if a.dest=='pass_through_args':
                    print(a)
            print("endsection")
        for a in self._actions:
            if 'dest' in zz.keys() and zz['dest'] =='pass_through_args':
                print(a)
            for aa in self.default_pass_through_args:
                if a.dest==sub("-","_",aa.strip("-")):
                    ddd=False
                    if a.default!=True:
                        dd("start section")
                        dd(zz)
                        dd(aa)
                        dd(a)
                        ddd=True
                    a.default=True
                    if ddd==True:
                        dd(a)
                        dd("end section")
            for aa in self.default_kw_pass_through_args.keys():
                if a.dest==sub("-","_",aa.strip("-")):
                    ddd=False
                    if a.default!=self.default_kw_pass_through_args[aa]:
                        dd("start section")
                        dd(zz)
                        dd(aa)
                        dd(a)
                        ddd=True
                    a.default=self.default_kw_pass_through_args[aa]
                    if ddd==True:
                        dd(a)
                        dd("end section")

    def print_help(self,*z):
        from pprint import pprint
        super().print_help()
        print()
        #print('###############')
        #print('## defaults: ##')
        #print('###############')
        #cols=get_terminal_size().columns
        #w=str(round(cols/3))
        #fs='{:' + w + '}{:' + w + '}'
        #for line in get_default_args(self,try_filter_unset=True):
        #    a=str(line[0]) if (len(line) >0) else "-"
        #    b=str(line[1]) if (len(line) >1) else "-"
        #    print( fs.format(a,b))
        #pprint(self.default_pass_through_args)
        #pprint(self.default_kw_pass_through_args)
        #print()
        txt = '##  orig. cmd help: "{}"  ##'.format(" ".join(self.wrapped_cmd))
        ltxt=len(txt)
        print("#"*ltxt)
        print(txt)
        print("#"*ltxt)
        print()
        call(self.wrapped_cmd+['-h'])
