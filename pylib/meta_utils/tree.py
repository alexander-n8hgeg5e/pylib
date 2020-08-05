def treewalk(node):
    """
    Walks a tree.
               \/  \/ \ \ \/  
     tree ->    \__ \ /  \/ 
                   \ | __/
                    \|/
                     |
             
    """
    d2go=['/mnt/1']                          
    leafes=[]                                 
    start=True                               
    while not len(d2go) == 0 or start==True: 
        start=False                          
        godir=d2go.pop()                     
        for d0,ds,fs in walk(godir):         
            for d in ds:                     
                d2go.append(d0+"/"+d)        
            for f in fs:                     
                files.append(d0+"/"+f)       
