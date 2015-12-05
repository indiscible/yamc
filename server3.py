from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import json

class JSONRPC:
    @staticmethod
    def Ping():
        return 'pong'
    
class RPC(object):
    @classmethod
    def GetProperties(c,**kwargs):
        r={}
        for p in kwargs["properties"]:
            print "looking for ", p
            if hasattr(c,p):
                print 'prop ', p
                r[p]= getattr(c,p)
        return r
    @classmethod
    def GetInfoBooleans(c,**kwargs):
        r={}
        for p in kwargs["booleans"]:
            name= "".join( p.split(".") )
            print "bool ",  p
            if hasattr(c, "".join( p.split(".") ) ):
                print "found ", name
                r[p]=True
        return r
    @classmethod
    def GetInfoLabels(c,**kwargs):
        r={}
        for p in kwargs["labels"]:
            name= "".join( p.split(".") )
            print "label ",  p
            if hasattr(c, name ):
                print "found ", name
                r[p]= getattr(c,name)
        return r
        
class Application(RPC):
    version= { 'major':15, 'tag':'stable', 'minor':2,'revision':'unknown'}
    volume= 50
    muted= False
    
class XBMC(RPC):
    SystemPlatformLinux= True
    SystemPlatformLinuxRaspberryPi= True
    SystemKernelVersion= "Open Source Media Center 2015.10-1"
    SystemBuildVersion= "15.2"
    
class Player(RPC):
    playerid=0
    _type="video"
    @classmethod
    def GetActivePlayers(c):
        return []   
        
def execute(j):
    c,m= j["method"].split(".")
    if ( globals().has_key(c) ):
        C= globals()[c]
        print "class ", C
        if hasattr( C, m ):
            print "method ", m
            if j.has_key("params"):
                print "params: ", j["params"]
                return getattr(C,m,)(**j["params"])
            else:
                return getattr(C,m)()
    return "Method Not found"

def execute(j):
    c,m= j["method"].split(".")
    C= globals()[c]
    if j.has_key("params"):
        return getattr(C,m)(**j["params"])
    else:
        return getattr(C,m)()

def reply(j):
    print "reply: ", j
    e= execute(j)
    print "execute: ", e
    return { "id": j["id"], "jsonrpc":"2.0", "result": execute(j) }

def error(code,message):
    return { "id": j["id"], "jsonrpc":"2.0", "error":
             { "code": code, "message": message } }

    
print getattr(Application,"GetProperties")(**{ 'properties':["version"]})

@Request.application
def server(request):
    print request
    print request.data
    try:
        r=[]
        j= json.loads(request.data)
        if isinstance(j,list):
            for jj in j:
                r.append(reply(jj))
        else:
            r= reply(j)            
    except ValueError as e:
        print e
        return Response( "", mimetype='application/json')
    return Response(  json.dumps(r), mimetype='application/json')


#if __name__ == '__main__':
run_simple('192.168.0.13', 8001, server)
