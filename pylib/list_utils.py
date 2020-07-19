
def equalize_lists(lists):
    # get the longest one
    maximum=0
    for l in lists:
        maximum=max(maximum,len(l))
    equal_lists=[]
    for l in lists.copy():  # modify l
        delta = maximum-len(l)
        if delta > 0 :
            l+=[l[-1]]*delta
        equal_lists.append(l)
    return equal_lists
    
