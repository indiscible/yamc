import subprocess
import event
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
    def GetProperties(c,properties):
        return c.Get(properties)

    @classmethod
    def GetInfoBooleans(c,booleans):
        return c.Get(booleans)
        
    @classmethod
    def GetInfoLabels(c,labels):
        return c.Get(labels)

    @classmethod
    def GetList(c,k,p,l):
        v= getattr(c,k)
        r= v[ l["start"]:l["end"] ]
        if p:
            r=[]
            for e in v[ l["start"]:l["end"] ]:
                r.append( { k:e[k] for k in p if e.has_key(k)} )
        return { k: r,
                 "limits":
                 { "start": 0, "end":len(r), "total":len(v) } }

class Settings(RPC):
    audiooutputpassthrough= False
    @classmethod
    def GetSettingValue(c,setting):
        name= "".join( setting.split(".") )
        if hasattr(c, name):
             return { setting:getattr(c,name) }

class Application(RPC):
    version= { 'major':15, 'tag':'stable', 'minor':2,'revision':'unknown'}
    volume= 50
    muted= False
    
    @classmethod
    def OnVolumeChanged(c):
        event.post( { "muted": c.muted, "volume": c.volume } )

def Mute():
    Application.muted= not Application.muted
    Application.OnVolumeChanged();
    

class XBMC(RPC):
    SystemPlatformLinux= True
    SystemPlatformLinuxRaspberryPi= True
    SystemKernelVersion= "Gilles"
    SystemBuildVersion= "0.0"


class Player(RPC):
    playerid=0
    _type="video"
    ffplay= None
    @classmethod
    def GetActivePlayers(c):
        return []
    @classmethod
    def Open(c,item):
        if c.ffplay:
            c.ffplay.terminate()
        s= AudioLibrary.songs[ item["songid"]-1 ]
        c.ffplay= subprocess.Popen(["ffplay","-i",s["file"]])  

class VideoLibrary(RPC):
    musicvideos= [ { "musicvideoid":1, "album":"emerald" } ]
    
    @classmethod
    def GetMovies(c,**p):
        print p
        return [ { "title": "indianajones", "file":"indiana.Avi" } ]
    @classmethod
    def GetTVShows(c,**p):
        return [ { "title": "seinfield", "file":"seinfield.Avi" } ]
    @classmethod
    def GetMusicVideos(c,properties,limits,sort=False):
        return c.GetList("musicvideos",properties,limits)

    
class AudioLibrary(RPC):
    genres= [ {"genreid":1,"title": "Rock", "thumbnail":"" },
              {"genreid":2,"title": "Jazz", "thumbnail":"" } ]
    artists=[ {"artist":"jimi", "artistid":1 },
              {"artist":"qunicy", "artisid":2 } ]
    albums= [ {"albumid":1, "albumlabel":"Are you experienced?" },
              {"albumid":2, "albumlabel":"fly" } ]
    songs= json.load( open("database/songs.json","r") )
    albums= json.load( open("database/albums.json","r") )
    artists= json.load( open("database/artists.json", "r") )
    @classmethod
    def GetArtists(c,limits,properties=[]):
        properties.append("artistid")
        properties.append("artist")
        properties= ["artist","artistid","thumbnail"]
        return c.GetList("artists",set(properties),limits)
    @classmethod
    def GetGenres(c,limits,properties=[]):
        properties.append("genreid")
        return c.GetList("genres",set(properties),limits)
    @classmethod
    def GetAlbums(c,limits,properties=[]):
        properties.append("albumid")
        properties=["albumid","albumlabel","title","thumbnail"]
        return c.GetList("albums",set(properties),limits)
    @classmethod
    def GetSongs(c,limits, properties=[]):
        print properties
        properties.append("songid")
        properties=["songid","title","track","rating","duration","albumid"]
        return c.GetList("songs",set(properties),limits)
    
class TVLibrary(RPC):
    @classmethod
    def GetMovies(c,**p):
        return [ { "title": "Hello", "file":"hello.Avi" } ]

class Files(RPC):
    @classmethod
    def GetSources(c,**p):
        print p, p.keys(), p.values()
        return {}
    @classmethod
    def GetDirectory(c,**p):
        print p, p.keys(), p.values()
        return {}
    
def handleudp():
    event.handleudp(globals(), locals())

def execute(j):
    c,m= j["method"].split(".")
    print c,m
    C= globals()[c]
    if j.has_key("params"):
        #print c,m,j["params"]
        return getattr(C,m)(**j["params"])
    else:
        #print c,m
        return getattr(C,m)()
