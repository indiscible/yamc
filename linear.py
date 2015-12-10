import json

d= json.load( open("record/jsonrpc(3)"))

def linearize(p,j):
    if isinstance(j,list):
        for k in j:
            linearize(p,k)
    elif isinstance(j,dict):
        for k in j.items():
            linearize(p+"/"+k[0], k[1])
    else:
        print p,":",j

linearize("",d)
