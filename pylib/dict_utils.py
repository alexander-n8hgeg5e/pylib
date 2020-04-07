from re import sub

def update_nested_dict(d1, d2):
    """
    Updates d1 with d2.
    The dict datatype wins over other datatypes.
    """
    if len(d2) > 0:
        d1keys=d1.keys()
        for k2 in d2.keys():
            def do():
                d1[k2]=d2[k2]
            if k2 in d1keys:
                if type(d1[k2]) is dict and type(d2[k2]) is dict:
                    # Key points to 2 dicts, need to go deeper.
                    d1[k2] = update_nested_dict(d1[k2] , d2[k2] )
                elif type(d2[k2]) is dict():
                    # Update existing key in d1 with a dict.
                    # The dict wins over other datatypes here.
                    do()
                else:
                    # Don't overwrite a dict, do nothing.
                    pass
            else:
                # Because key is not in d1,
                # there is no doubt that "do" is the right choice. 
                do()
        return d1
    else:
        return d1
