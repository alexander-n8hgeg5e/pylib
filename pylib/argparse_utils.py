from argparse import Action,ArgumentParser,ArgumentDefaultsHelpFormatter
from argparse import _StoreTrueAction,SUPPRESS
from subprocess import call
from os import get_terminal_size
from os.path import basename
from re import sub
#from pylib.du import dd
from sys import argv,stderr

class unused_folded():
    pass
    #class Action_convert(Default_help_action):
    #    def __call__(self, parser, namespace, values, option_strings):
    #        if self.dest in parser.conversions.keys():
    #            conv=parser.conversions[self.dest]
    #            _d,_v,_o=self.dest,option_strings,values
    #            #if len(_v) is 0 or (len(_v) is 1 and _v[0] is None):
    #            #    _v=self.default
    #            #    d("d1")
    #            #    d(_v)
    #            d,v,o=conv(_d,_o,_v)
    #            setattr(namespace,d,v)
    #class Action_add_pass_through_arg(Default_help_action):
    #    def __init__(self, *z, nargs=0, **zz):
    #        super().__init__(*z, nargs=nargs, **zz)
    #    def __call__(self, parser, namespace, values, option_string):
    #        if self.dest in parser.dest_no_pass_through:
    #            return
    #        for val in values:
    #            if val in parser.dest_no_pass_through:
    #                return
    #        #dd(self.dest)
    #        if self.dest == "pass_through_args":
    #            for v in values:
    #                if not v in namespace.pass_through_args:
    #                    #dd(v)
    #                    # add whatever it is
    #                    namespace.pass_through_args.append(v)
    #        else:
    #            if not any(os in namespace.pass_through_args for os in self.option_strings):
    #                key="--"+sub('_','-',self.dest)
    #                namespace.pass_through_args.append(key)
    #            setattr(namespace,self.dest,True)
    #
    #class Action_add_kw_pass_through_arg(Default_help_action):
    #    def __init__(self, *z, nargs=None, **zz):
    #        super().__init__(*z, nargs=nargs, **zz)
    #    def __call__(self, parser, namespace, values, option_string):
    #        if self.dest in parser.dest_no_pass_through:
    #            return
    #        if self.dest == "kw_pass_through_args":
    #            for v in values:
    #                if not v in namespace.kw_pass_through_args:
    #                    # add whatever it is
    #                    namespace.kw_pass_through_args.update({option_string:v})
    #        else:
    #            if not self.const is None:
    #                val=self.const
    #            else:
    #                val=values
    #            key="--"+sub('_','-',self.dest)
    #            dd(key)
    #            namespace.kw_pass_through_args.update({key:val})
    #            setattr(namespace,self.dest,val)
    #            #setattr(parser._actions[''],self.dest,val)
    #
    #class Action_remove_pass_through_arg(Default_help_action):
    #    def __init__(self,*z,nargs=0,**zz):
    #        super().__init__(*z,nargs=nargs,**zz)
    #    def __call__(self, parser, namespace, values, option_string):
    #        if self.dest in parser.dest_no_pass_through:
    #            return
    #        if self.dest in "pass_through_args":
    #            # no remove support here
    #            return
    #        else:
    #            for os in self.option_strings:
    #                osr="-"+os.strip("-n")
    #                if osr in namespace.pass_through_args:
    #                    namespace.pass_through_args.remove(osr)
    #                osr="--" + os.strip("--no-")
    #                if osr in namespace.pass_through_args:
    #                    namespace.pass_through_args.remove(osr)
    #            setattr(namespace,self.dest,False)
    pass

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

class Action_no_pass_through(Action):
    pass_arg_through=False

class Default_help_action(Action):
    default_help=' (default: %(default)s)'
    def __init__(self,*z,help="",default=None,**zz):
        if not default is None:
            help=help+self.default_help
        super().__init__(*z,help=help,default=default,**zz)

class Action_add_pass_through_args(Default_help_action):
    def __call__(self, parser, namespace, values, option_string):
        if self.dest in parser.dest_no_pass_through:
            return
        setattr(namespace, self.dest, values)

class Action_disable():
    def __new__(self,what):
        class Action_disable(Default_help_action,Action_no_pass_through):
            def __init__(self,*z,**zz):
                super().__init__(*z,nargs=0,**zz)
            def __call__(self, parser, namespace, values, option_string):
                if what in namespace:
                    setattr(namespace,what,False)
        return Action_disable

class Action_enable():
    def __new__(self,what):
        class Action_enable(Default_help_action,Action_no_pass_through):
            def __init__(self,*z,**zz):
                super().__init__(*z,nargs=0,**zz)
            def __call__(self, parser, namespace, values, option_string):
                if what in namespace:
                    setattr(namespace,what,True)
        return Action_enable

class Action_set():
    def __new__(self,what,*z):
        class Action_set(Default_help_action,Action_no_pass_through):
            def __call__(self, parser, namespace, values, option_string):
                if what in namespace:
                    set_to=" ".join(values if len(z)==0 else z)
                    setattr(namespace,what,set_to)
        return Action_set

class Action_store_true_no_pass(_StoreTrueAction,Action_no_pass_through):
    def __call__(self, parser, namespace, values, option_strings):
        parser.do_not_pass_through(self.dest)
        super().__call__(parser, namespace, values, option_strings)

class PassThroughHelpFormater(ArgumentDefaultsHelpFormatter):
    pass
    #def add_usage(self, usage, actions, groups, prefix=None):
    #    if usage is not SUPPRESS:
    #        args = usage ,actions, groups, prefix
    #        self._add_item(self._format_usage, args)

class PassThroughArgumentParser(ArgumentParser):
    """
    supply wrapped cmd as list like: [cmd,subcmd,...]
    """
    def __init__(self, *z, prog=None, wrapped_cmd=[], dest_no_pass_through=[], output_conversions={},debug=False, **zz):
        self.debug=debug
        self.dest_no_pass_through=dest_no_pass_through
        self.wrapped_cmd=wrapped_cmd
        self.output_conversions=output_conversions
        prog=basename(argv[0])
        if len(wrapped_cmd)> 1: 
            prog += " "+"["+"] [".join(wrapped_cmd[1:])+"]"
            self.dest_no_pass_through.extend(wrapped_cmd[1:])
        super().__init__( 
                            *z,
                            prog=prog,
                            formatter_class=PassThroughHelpFormater,
                            **zz,
                        )
        #self.add_argument(dest="pass_through_args",nargs="*",action=Action_add_pass_through_args,default=False)
        self.parsed_args=None

    def _add_action(self,action):
        ret_action=super()._add_action(action)
        if hasattr(ret_action,'pass_arg_through') and not ret_action.pass_arg_through:
            self.do_not_pass_through(ret_action.dest)
        return ret_action 

    def _long_arg_to_dest(self,dest):
        retval=sub('-','_',dest.strip("-"))
        return retval
            
    def _dest_to_long_arg(self,la):
        retval="--"+sub('_','-',la)
        return retval
            
    def prepare_pass_through_args(self,args):
        if self.debug:
            from pprint import pformat
            print("\ninput prepare_pass_through_args(non-kw-args):",file=stderr)
            if len(args)>0:
                for arg in args:
                    print("    "+arg,file=stderr)
            else:
                print("    no non-kwargs",file=stderr)
        _args=args
        args=[]
        for a in _args:
            if not a in dest_no_pass_through:
                args.append(a)
                if a in self.output_conversions.keys():
                    args+=[self.output_conversions[i](i,None)]
                else:
                    args+=["--"+arg]
        if self.debug:
            from pprint import pformat
            print("output prepare_pass_through_args(non-kw-args):",file=stderr)
            if len(args)>0:
                for arg in args:
                    print("    "+arg,file=stderr)
            else:
                print("    nothing here",file=stderr)
        return args

    def prepare_kw_pass_through_args(self,kwargs):
        if self.debug:
            from pprint import pformat
            print("\ninput prepare_kw_pass_through_args:",file=stderr)
            if len(kwargs)>0:
                for i,j in kwargs:
                    print("    "+i+(20-len(i))*" "+" = "+repr(j),file=stderr)
            else:
                print("    no kwargs")
        l=[]
        for i,j in kwargs:
            if i=="pass_through_args":
                continue
            if i in self.dest_no_pass_through:
                continue
            if j is None:
                continue
            if i in self.output_conversions.keys():
                l+=[self.output_conversions[i](i,j)]
            else:
                if type(j) is bool:
                    if j:
                        l+=[self._dest_to_long_arg(i)]
                    else:
                        continue
                elif type(j) is list:
                    l+=[self._dest_to_long_arg(i)]+j
                else:
                    l+=[self._dest_to_long_arg(i),j]
        if self.debug:
            from pprint import pformat
            print("output prepare_kw_pass_through_args:",file=stderr)
            if len(kwargs)>0:
                for j in l:
                    print("    "+repr(j),file=stderr)
            else:
                print("    nothing here")
        return l

    def _arg_is_value(arg):
        lnext=len(arg)
        if arg[0] != "-" \
            or match('^[-][0-9]+[a-zA-Z]?$',anext):
                    return True
        return False

    def do_not_pass_through(self,dest_or_optionstr):
        dest=sub('-','_',dest_or_optionstr.strip("-"))
        if not dest in self.dest_no_pass_through:
            self.dest_no_pass_through.append(dest)

    def parse_args(self, args=None, namespace=None):
        namespace , argv = self.parse_known_args(args, namespace)
        if self.debug:
            from pprint import pformat
            print("\nraw parsed args:",file=stderr)
            for k,v in (namespace).__dict__.items():
                print("    "+k+(20-len(k))*" "+" = "+repr(v),file=stderr)
        #l=len(argv)
        #skip=0
        #for i in range(l):
        #    if skip > 0:
        #        skip-=1
        #        continue
        #    if argv[check][0]=="-":
        #        j=i+1
        #        while j < l and self._arg_is_value(argv[j]):
        #            # kwarg
        #            skip+=1
        #    if skip == 0:
        #        # no kwarg here
        _argv=argv
        argv=[]
        for a in _argv:
            if not a.strip("-") in self.dest_no_pass_through:
                argv.append(a)
        
        setattr(namespace,'pass_through_args',argv)
        self.parsed_args=namespace
        if self.debug:
            from pprint import pformat
            print("actual \"real pass-through\" args after filter:",file=stderr)
            if len(argv)>0:
                for a in argv:
                    print("    "+repr(a),file=stderr)
            else:
                print("nothing here",file=stderr)
        return namespace

    def get_prepared_args(self):
        if self.parsed_args is None:
            self.parse_args()
        kwargs=self.prepare_kw_pass_through_args(self.parsed_args._get_kwargs())
        args=self.prepare_pass_through_args(self.parsed_args._get_args())
        preped_args=args+kwargs+self.parsed_args.pass_through_args
        if self.debug:
            from pprint import pformat
            print("\nprepared_args:",file=stderr)
            for line in pformat(preped_args).split("\n"):
                print("    "+line,file=stderr)
        return preped_args
        
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

# vim: foldmethod=indent foldlevel=0 foldnestmax=2:
