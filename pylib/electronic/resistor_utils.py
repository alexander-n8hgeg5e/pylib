from re import sub,match

def _resistor_string_sub_symbols(s):
    s=sub('([ ]|^)([^ ]+)[kK]','\\1(\\2)*1000',s)
    s=sub('([ ]|^)([^ ]+)[mM]','\\1(\\2)*1000000',s)
    return s

def resistor_string_to_float(s,enable_mult=False):
    if type(s) is str:
        if enable_mult:
            parts=s.split(' ')
            sl=[]
            for part in parts:
                if match('^\\d+[xX][^ ]+$',part):
                    d=sub('^(\\d+)[xX][^ ]+$','\\1',part)
                    d=int(d)
                    obj=sub('^\\d+[xX]([^ ]+)$','\\1',part)
                    sl+=([obj]*d)
                else:
                    sl.append(part)
            for i in range(len(sl)):
                sl[i]=float(eval(_resistor_string_sub_symbols(sl[i])))
            s=sl
        else:
            s=float(eval(_resistor_string_sub_symbols(s)))
    else:
        s=float(s)
    return s
