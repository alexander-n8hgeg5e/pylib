
class IndentationParser():
    @staticmethod
    def _get_depth(line):
        len_strip = len(line.lstrip())
        len_nostrip = len(line)
        return len_nostrip-len_strip

    @staticmethod
    def _prepare_lines(lines):
        _lines=[]
        for line in lines:
            if len(line.strip())>0:
                _lines.append(line)
        return _lines

    def __init__(self,data,linesep="\n"):
        self.linesep = linesep
        if type(data) is str:
            self.lines = data.split(linesep)
        elif type(data) is bytes:
            self.lines = data.split(linesep.encode())
        else:
            raise Exception(TypeError("Type {} not supported".format(type(lines))))
        self.levels  = []
        self.data    = []

    def _get_lowest_level_width(self):
        lowest=0
        for line in self.lines:
            depth=type(self)._get_depth(line)
            lowest=min(depth,lowest)
        return lowest

    def _get_deepest_level(self):
        lsl = len(self.levels)
        if lsl > 0:
            return lsl - 1
        else:
            return None

    def _append_data(self,level,data):
        #print('append: level={} ,data={}'.format(level,data))
        thing = self.data
        for i in range(level):
            if type(thing[-1]) is list:
                thing = thing[-1]
            else:
                thing[-1] = []
                thing = thing[-1]
        thing.append([data.strip()])
    
    def _get_level(self,depth,line):
        if line.find(b"Name:") != -1 or line.find(b"Argument:") != -1:
            print('d={} , line={}'.format(depth,line))
        deepest = self._get_deepest_level()
        for i in range(deepest + 1):
            if self.levels[i] == depth:
                return i
        return None

    def parse(self):
        self.levels.append( self._get_lowest_level_width() )
        self.lines = IndentationParser._prepare_lines(self.lines)
        for line in self.lines:
            depth = type(self)._get_depth(line)
            deepest_level = self._get_deepest_level()
            if depth > self.levels[deepest_level]:
                self.levels.append(depth)
            self._append_data(self._get_level(depth,line),line)
        #from pprint import pprint
        #pprint(self.data)
