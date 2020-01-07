
class R(bytes):
    def __new__(cls,z,**zz):
        if type(z) is str:
            z=z.encode()
        obj = super().__new__(cls,z)
        return obj
        
    def __init__(self,z,ngroups=0,**zz):
        bytes.__init__(z,**zz)
        self.ngroups=ngroups

    def g(self):
        self.ngroups+=1
        return R('(') + self + R(')')

    def __or__(self,value):
        return R(R("|").join((self,value))).g()

    def __ror__(self,value):
        return R(R("|").join((value,self))).g()

    def __radd__(self,value):
        return value.__add__(self)

    def __add__(self,value):
        if not type(value) in [R,Ex,C]:
            value=R(value)
        return R(super().__add__(value), ngroups=self.ngroups+value.ngroups)

    def n(self,*z):
        if z[0] in ('*','+','?'):
            return self.g() + z[0]
        elif len(z) == 1 and hasattr(z[0],'__int__'):
            i=int(z[0])
            if i > 0:
                return self.g() + '{'+str(i)+'}'
        elif len(z) == 2:
            if hasattr(z[0],'__int__') and hasattr(z[1],'__int__'):
                return self.g() + '{'+str(int(z[0]))+','+str(int(z[1]))+'}' 
        raise Exception("incorrect args: "+str(z) )

class Ex(R):
    def __new__(cls,chars):
        return super().__new__(cls,'[^'+chars+']')

class C(R):
    def __new__(cls,chars):
        return super().__new__(cls,'['+chars+']')
