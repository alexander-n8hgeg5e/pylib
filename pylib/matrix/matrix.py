#!/usr/bin/python3
# Copyright 2019 Alexander Wilhelmi
# This file is part of pylib.
# 
# pylib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pylib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pylib.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil von pylib.
# 
# pylib ist Freie Software: Sie können es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
# veröffentlichten Version, weiter verteilen und/oder modifizieren.
# 
# pylib wird in der Hoffnung, dass es nützlich sein wird, aber
# OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License für weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.
# Copyright 2019 Alexander Wilhelmi
# This file is part of pylib.
# 
# pylib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pylib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pylib.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil von pylib.
# 
# pylib ist Freie Software: Sie können es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
# veröffentlichten Version, weiter verteilen und/oder modifizieren.
# 
# pylib wird in der Hoffnung, dass es nützlich sein wird, aber
# OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License für weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.

class Formular():
    ops=[
            ('add','+'),
            ('sub','-'),
            ('mul','*'),
            ]
    def _enum_ops(self):
        self.num2op = []
        for i in range(len(self.ops)):
            self.num2op.append(self.ops[i])
            exec('self.' + self.ops[i][0] + '=' + str(i) ) 
    def __init__(self,a,op,b):
        if type(op) != int:
            raise TypeError('op need to be type "int"')
        self._enum_ops()
        self.a=a
        self.op=op
        self.b=b
    def __add__(self,b):
        if b==0:
            return self
        else:
            return Formular(self,self.add,b)
    def __radd__(self,b):
        if b==0:
            return self
        return Formular(b,self.add,self)
    def __mul__(self,b):
        if b==1:
            return self
        elif b==0:
            return 0
    def __rmul__(self,b):
        if b==1:
            return self
        elif b==0:
            return 0
        else:
            return Formular(b,self.mul,self)
    def __str__(self):
        return '('+str(self.a)+self.num2op[self.op][1]+str(self.b)+')'

class Variable():
    ops=Formular.ops
    def __init__(self,name):
        Formular._enum_ops(self)
        self.name=name
    def __str__(self):
        return self.name
    def __add__(self,b):
        if b==0:
            return self
        return Formular(self,self.add,b)
    def __radd__(self,b):
        if b==0:
            return self
        else:
            return Formular(b , self.add , self)
    def __mul__( self, b ):
        if b==0:
            return 0
        elif b==1:
            return self
        else:
            return Formular( self, self.mul , b )
    def __rmul__(self, b):
        if b==0:
            return 0
        elif b==1:
            return self
        else:
            return Formular(b,self.mul,self)

class MatrixElement():
    def __init__(self, e):
        if type(e) == MatrixElement:
            raise TypeError("unsupported type of value for MatrixElement: "+str(type(e)))
        if e.__class__.__name__ == 'NotImplementedType':
            raise TypeError('type not good bro')
        self.value = e
        self.print_w = 1
        self.alignment='^'
        self.print0=True
    def __format__(self,format):
        if self.value == 0:
                if not self.print0:
                    return ' '* self.print_w
                else:
                    return ('{:'+self.alignment+'-'+str(self.print_w)+'.0f}').format(self.value)
        elif self.value == None:
               return ' '* self.print_w
        elif type(self.value) == str:
            return ('{:'+self.alignment+''+str(self.print_w)+'s}').format(self.value)
        elif type(self.value) == Formular or type(self.value)==Variable:
            return str(self.value)
        elif type(self.value) == float:
            if self.value%1 == 0:
                return ('{:'+self.alignment+'-'+str(self.print_w)+'.0f}').format(self.value)
            else:
                return ('{:'+self.alignment+'-'+str(self.print_w)+'.1f}').format(self.value)
        elif type(self.value) == int:
            return ('{:'+self.alignment+'-'+str(self.print_w)+'.0f}').format(self.value)
        else:
            #return str(self.value)[0:self.print_w]
            raise TypeError("unsupported type of value in MatrixElement: "+self.value.__repr__())
    def __str__(self):
        #p2(type(self.value))
        return self.__format__('')
    def __repr__(self):
        return self.__format__('')
    def update_print_width(self,val=None):
        if val is not None:
            self.print_w = val
        l=len(self.__format__(''))
        if l > self.print_w:
            self.print_w = l
    def __print_print_width__(self,indent=0):
        p2(indent * ' '+'element pw: ')
        p2(' '* indent + str(self.print_w))
    def __print_elements__(self,indent,attr=None):
        try:
            print(indent * ' '+ 'own type: '+str(self.__class__.__name__),file=out2)
        except AttributeError:
            print(indent * ' '+''+attr+': no such attribute',file=out2)
        if not attr is None:
            try:
                print(indent * ' '+''+attr+': '+str(self.__getattribute__(attr)),file=out2)
            except AttributeError:
                print(indent * ' '+''+attr+': no such attribute',file=out2)
        print(' '* indent + '>'+self.__str__()+'<',file=out2)
    def __set_elements_attributes__(self,name,val):
        self.__setattr__(name,val)
    def __lt__(self,*args,**kwargs):
        return self.value.__lt__(*args, **kwargs)
    def __gt__(self,*args,**kwargs):
        return self.value.__gt__(*args, **kwargs)
    
    # math operations

    def __sub__(self,val,*args,**kwargs):
        if type(val)== MatrixElement:
            return MatrixElement( self.value - val.value )
        else:
            return MatrixElement( self.value - val)

    def __rsub__(self,val,*args,**kwargs):
        if type(val)== MatrixElement:
            return MatrixElement( val.value - self.value )
        else:
            return MatrixElement( val - self.value)

    def __add__(self,val,*args,**kwargs):
        if type(val)== MatrixElement:
            return MatrixElement( self.value + val.value )
        else:
            return MatrixElement( self.value + val )

    def __mul__(self,val,*args,**kwargs):
        if type(val) == MatrixElement:
            return MatrixElement( self.value * val.value)
        else:
            return MatrixElement( self.value * val)

    def __radd__(self,val,*args,**kwargs):
        if type(val)== MatrixElement:
            return MatrixElement( val.value + self.value)
        else:
            return MatrixElement( val + self.value )
    # type conversions
    def __int__(self,*args,**kwargs):
        return int(self.value)
    def __float__(self,*args,**kwargs):
        return float(self.value)

class Matrix(list):
    def __init__( self, *args, **kwargs ):
        stack = traceback.extract_stack()
        filename, lineno, function_name, code = stack[-2]
        var_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
        self.matrixname=var_name
        super().__init__( *args, **kwargs )
        self.matrixname = ''
        self.print_w = 0
        self.line_print_w = 0
        self.sep=' '
        self.line_sep=' '
        self.end = '|'
        self.start = '|'
        self.headline_char = '-'
        self.footline_char = '-'
        self.corner_lt = "*"
        self.corner_rt = "*"
        self.corner_lb = "*"
        self.corner_rb = "*"
        self.space=' '
        self.__convert_all__()
        self.update_print_width()
        self.update_line_print_width()
    def __convert_all__(self):
        for i in range(len(self)):
            item=super().__getitem__(i)
            t = type(item)
            if t != MatrixElement and t != Matrix:
                self.__convert_value__(i)
            elif t==Matrix:
                item.__convert_all__()
        is_vector = True
        for i in self:
            if type(i) != MatrixElement:
                is_vector = False
        self.is_vector = is_vector
    def __update__(self):
        is_vector = True
        for i in self:
            if type(i) != MatrixElement:
                is_vector = False
        self.is_vector = is_vector
    def __convert_value__(self,i):
        t = type(super().__getitem__(i))
        #print('convert value: '+str(super().__getitem__(i))+' type: '+t.__name__,file=out2)
        if t != list and t != Matrix and t !=MatrixElement :
            super().__setitem__(i, MatrixElement( super().__getitem__(i) ))
        elif t == list:
            super().__setitem__(i, Matrix( super().__getitem__(i) ))
    def update_print_width(self,val=None):
        """
        gets the max width of all elements
        matrix needs even spaceing in all direction
        to get nice view of diagonals and stuff like that
        """
        if val is not None:
            self.print_w = val
            for i in self:
                classname=i.__class__.__name__
                if classname == 'int':
                    print(i.__class__.__name__,file=out2)
                    print(self.__class__.__name__,file=out2)
                    print(i,file=out2)
                    print(self.is_vector,file=out2)
                    print(len(self),file=out2)
                i.update_print_width(val)
        else:
            for i in self:
                if type(i) == Matrix or type(i) == MatrixElement:
                    i.update_print_width()
                    if i.print_w > self.print_w:
                        self.print_w = i.print_w
            for i in self:
                if type(i) == Matrix or type(i) == MatrixElement:
                    i.update_print_width(self.print_w)
    def update_line_print_width(self,val=None):
        if val is not None:
            self.line_print_w = val
            if not self.is_vector:
                  for i in self:
                      i.update_line_print_width(val)
        else:
            if self.is_vector:
                """
                there should be only MatrixElement(s) in it.
                """
                l=len(self.__str__().strip())
                if l > self.line_print_w:
                      self.line_print_w=l
            else:
                # self update with highest one
                for i in self:
                    if type(i) == Matrix:
                        i.update_line_print_width()
                        if i.line_print_w > self.line_print_w:
                            self.line_print_w = i.line_print_w
                # update the others
                for i in self:
                    if type(i) == Matrix:
                        i.update_line_print_width(self.line_print_w)
    def __str__(self):
        self.__convert_all__()
        self.update_print_width()
        l=len(self)
        if self.is_vector:
            line = self.start + self.space
            for i in range(l):
                line = line + self[i].__str__()
                if not i == l - 1:
                    line = line + self.sep
            line = line + self.space + self.end + nl
            return line
        else:
            sepline,headline,footline=self.__gen_sepheadfootline__()
            lines=  headline
            #lines=lines+sepline
            for i in range(l):
                if not i == l - 2:
                    line =  self[i].__str__()
                else:
                    line = self[i].__str__().strip()[:-len(self.end)] + str(l) + nl
                lines = lines + line
            lines=lines + footline
            return lines
    def __gen_sepheadfootline__(self):
        self.update_line_print_width()
        line_lenght = self.line_print_w
        mid_header_len = line_lenght - len(self.start) - len(self.end) - len(self.matrixname)
        pre_header_len = 2 + _int( 5 * (mid_header_len/2) / 100 )
        post_header_len = mid_header_len - pre_header_len
        c_info = str(_len(self[0]))
        headline = self.corner_lt + pre_header_len * self.headline_char \
                   + self.matrixname + self.headline_char * post_header_len + self.corner_rt + nl
        mid_footer_len = line_lenght - len(self.start) - len(self.end) - len(c_info)
        post_footer_len = 2 + _int( 5 * (mid_footer_len/2) / 100 )
        pre_footer_len = mid_footer_len - post_footer_len
        footline = self.corner_lb + pre_footer_len * self.footline_char  \
                  + c_info + post_footer_len * self.footline_char + self.corner_rb +nl
        sepline = self.start + self.line_sep * ( line_lenght - len(self.start) - len(self.end)) + self.end + nl
        return sepline,headline,footline
    def __print_elements__(self,indent=0,attr=None):
        l=[]
        #print(indent * ' '+'Matrix member elements: '+ self.__class__.__name__,file=out2)
        print(indent * ' '+'Matrix member elements: ',file=out2)
        if not attr is None:
            try:
                print(indent * ' '+attr+': '+str(self.__getattribute__(attr)),file=out2)
            except AttributeError:
                print(indent * ' '+attr+': no such attribute',file=out2)
        for i in self:
            if type(i) == Matrix or type(i) == MatrixElement:
                   i.__print_elements__(indent + 16,attr=attr)
            else:
                if type(i) == list:
                    print(indent * ' '+ 'listmember: '+str(j),file=out2)
                    for j in i:
                        print((16+indent) * ' '+ 'member of type: '+str(j.__class__.__name__)+' with content: '+str(j),file=out2)
                else:
                    print((16+indent) * ' '+ 'member of type: '+str(i.__class__.__name__)+' with content: '+str(i),file=out2)
    def __set_elements_attributes__(self,name,val):
        for i in self:
            if type(i) == Matrix or type(i) == MatrixElement:
                i.__set_elements_attributes__(name,val)
    def __print_print_width__(self,indent=0):
        l=[]
        p2(indent * ' '+'own pw: ')
        for i in self:
            p2(indent * ' '+'member_pw: ')
            i.__print_print_width__(indent + 16)
    def __print_line_print_width__(self,indent=0):
        l=[]
        p2(indent * ' ' + 'own line pw: '+ str(self.line_print_w))
        for i in self:
            if type(i) != MatrixElement: 
                p2(indent * ' '+'member_line_pw: ')
                i.__print_line_print_width__(indent+16)
    def __mul__(self,M2,*args,**kwargs):
        M=[]
        M1=self
        h1=len(M1)
        h2=len(M2)
        w1=len(M1[0])
        w2=len(M2[0])
        for row_1 in range(h1):
            row=[]
            for col_2 in range( w2 ):
                s=0
                for k in range( w1):
                    s = (M1[row_1][k] * M2[k][col_2]) + s
                row.append(s)
            M.append(row)
        return M
    def __add__(self,val,*args,**kwargs):
        return Matrix(super().__add__(list(val),*args,**kwargs))
    def joinb(self,M):
        return super().extend(M)
    def __getitem__(self,i,*args,**kwargs):
        item = super().__getitem__(i,*args,**kwargs)
        t = type(item)
        if  t != Matrix and t != MatrixElement:
            if t == list:
                 r = Matrix(item)
            else:
                 r = MatrixElement(item)
        else:
            r=item
        self[i] = r
        return   r
    def __setitem__(self,i,val,*args,**kwargs):
        t = type(val)
        if t != Matrix and t != MatrixElement and t != list:
            return super().__setitem__(i,MatrixElement(val))
        elif t == list:
            return super().__setitem__(i,Matrix(val),*arg,**kwargs)
        elif t== Matrix or t== MatrixElement:
            super().__setitem__(i, val)
    def __iter__(self,*args,**kwargs):
        for i in range(super().__len__()):
            t = type(super().__getitem__(i))
            if t != Matrix and t != MatrixElement:
                    self.__convert_value__(i)
            yield self[i]
