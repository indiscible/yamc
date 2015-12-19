import requests


class intercept(type):
    def __getattr__(s,name):
        print name

class J:
    __metaclass__= intercept
    def yop():
        print "yop"

class K:
    
    def __init__(s,dest):
        s.method=""
        s.dest=dest

    def __getattr__(s,name):
        sep="." if len(s.method) else ""
        s.method+=sep+name
        return s
            
    def __call__(s,*p,**q):
        json={ "id":0, "method":s.method }
        if len(q): json["params"]= q
        print json
        s.method=""
        r= requests.post(s.dest,json=json)
        try:
            return r.json()["result"]
        except ValueError:
            return r.text
            
        

k= K("http://192.168.0.13:8001")

print k.Player.GetActivePlayers()

