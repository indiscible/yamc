from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import json

class JSONRPC:
    @staticmethod
    def Ping():
        return 'pong'
    
class RPC(object):
    @classmethod
    def Get(c,ps):
        r={}
        for p in ps:
            name= "".join( p.split(".") )
            if hasattr(c, name ):
                r[p]= getattr(c,name)
        return r
            
    @classmethod
    def GetProperties(c,**kwargs):
        return c.Get(kwargs["properties"])

    @classmethod
    def GetInfoBooleans(c,**kwargs):
        return c.Get(kwargs["booleans"])
        
    @classmethod
    def GetInfoLabels(c,**kwargs):
        return c.Get(kwargs["labels"])
    
class Application(RPC):
    version= { 'major':15, 'tag':'stable', 'minor':2,'revision':'unknown'}
    volume= 50
    muted= False
    
class XBMC(RPC):
    SystemPlatformLinux= True
    SystemPlatformLinuxRaspberryPi= True
    SystemKernelVersion= "Gilles"
    SystemBuildVersion= "0.0"
    
class Player(RPC):
    playerid=0
    _type="video"
    @classmethod
    def GetActivePlayers(c):
        return []

class VideoLibrary(RPC):
    @classmethod
    def GetMovies(c,**p):
        print p
        return [ { "title": "indianajones", "file":"indiana.Avi" } ]
    @classmethod
    def GetTVShows(c,**p):
        return [ { "title": "seinfield", "file":"seinfield.Avi" } ]
    @classmethod
    def GetMusicVideos(c,**p):
        return [ { "title":"Dry", "artist":"PJ Harvey" } ]
 
class AudioLibrary(RPC):
    @classmethod
    def GetArtists(c,**p):
        return [ { "description":"jimi hendriw"} ]
    @classmethod
    def GetGenres(c,**p):
        return [ { "title":"rock", "thumbnail":"rock.jpeg"} ]
    @classmethod
    def GetAlbums(c,**p):
        return [ { "title":"Are You Experienced", "artist":"jimi hendriw"} ]
    @classmethod
    def GetSongs(c,**p):
        return [ { "title":"Hey Joe", "track":1} ]
    
class TVLibrary(RPC):
    @classmethod
    def GetMovies(c,**p):
        return [ { "title": "Hello", "file":"hello.Avi" } ]

    
def execute(j):
    c,m= j["method"].split(".")
    C= globals()[c]
    if j.has_key("params"):
        return getattr(C,m)(**j["params"])
    else:
        return getattr(C,m)()

def reply(j):
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
    r= json.dumps(r)
    print r
    return Response(  r, mimetype='application/json')


#if __name__ == '__main__':
run_simple('192.168.0.13', 8001, server)
