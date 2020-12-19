


class Data():
    def __init__( self, data, encoding='utf8',byteorder="big" ):
        self.encoding=encoding
        self.byteorder=byteorder
        self.data=data

    def _convert(self):
        data=self.data
        dtype = type(data)
        if dtype == bytes:
            pass
        elif dtype == str:
            if not self.encoding is None:
                data = data.encode(encoding=self.encoding )
            else:
                data = data.encode(data)
        elif dtype == int:
             lh=len(str(hex(data))[2:])
             data=data.to_bytes(int(lh/2),self.byteorder)
        if not type(data) is bytes:
            from sys import stderr
            print("type(data)={}\ndata={}".format(type(data),data),file=stderr)
            raise Exception("Error: need bytes")
        self.data = data

    def int(self):
        if type(self.data) is int:
            return self.data
        else:
            self._convert()
        i=0
        for j in range(len(self.data)):
            i += self.data[-j-1] * 256 ** j
        return i

    def bytes(self):
        if type(self.data) is bytes:
            return self.data
        else:
            self._convert()
        return self.data
    
    def str(self):
        if type(self.data) is str:
            return self.data
        else:
            self._convert()
        return self.data.decode( encoding = self.encoding )

    @classmethod
    def selftest(cls):
        from types import MethodType
        convertions_to_test=[
            "hello",
            b"hello",
            448378203247,]
        for i in convertions_to_test:
            c=cls(i)

            method_names=[(m if len(m)>0 and m[:1]!="_" and not m == "selftest" else None) for m in dir(c)]
            while None in method_names:
                method_names.pop(method_names.index(None))

            things=[getattr(c,f) for f in method_names]
            functions=[f if type(f) is MethodType else None for f in things]
            while None in functions:
                functions.pop(functions.index(None))

            for f in functions:
                if not f is None:
                    v=f()
                    if not v in convertions_to_test:
                        return False
            return True





