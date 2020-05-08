from pylib.decorators.deprecated.verbosity_decorators import Subprocess_Popen_init_VerbosityDecorator
from pylib.decorators.deprecated.verbosity_decorators import Subprocess_check_call_VerbosityDecorator_v2 as Subprocess_check_call_VerbosityDecorator
from pylib.decorators.deprecated.verbosity_decorators import Subprocess_call_VerbosityDecorator_v2 as Subprocess_call_VerbosityDecorator
from pylib.decorators.deprecated.verbosity_decorators import Subprocess_check_output_VerbosityDecorator_v2 as Subprocess_check_output_VerbosityDecorator

from subprocess import check_output,check_call,DEVNULL,call,Popen,CalledProcessError

for thing in [ 'call','check_call','Popen', 'check_output' ]:
    exec( "from subprocess import " + thing + " as subprocess_" + thing )


@Subprocess_check_call_VerbosityDecorator
def check_call(*z,**zz):
        return subprocess_check_call(*z,**zz)

@Subprocess_check_output_VerbosityDecorator
def check_output(*z,**zz):
    return subprocess_check_output(*z,**zz)

@Subprocess_call_VerbosityDecorator
def call(*z,**zz):
        return subprocess_call(*z,**zz)

class Popen(subprocess_Popen):
    def __init__(self,*z,**zz):
        dec = Subprocess_Popen_init_VerbosityDecorator(super().__init__)
        dec.__call__(*z,**zz)
    
