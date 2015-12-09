import subprocess
import event
import json
import vlc

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
    def GetProperties(c,properties,**o):
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

def subdict(d,p):
    return { k:d[k] for k in p if d.has_key(k) }
    
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
    print "Init Player class ----------------"
    playerid=0
    _type="video"
    itemid=-1
    @classmethod
    def GetActivePlayers(c):
        return [{"playerid":c.playerid, "type":c._type}]
    @classmethod
    def Open(c,item):
        c.itemid= item["songid"]
        s= AudioLibrary.songs[ c.itemid ]
        r= vlc.play(s["file"])
        c._type= "audio"
        c.playerid=0
        stream= r["information"]["category"]["Stream 0"]
        XBMC.MusicPlayerCodec= stream["Codec"]
        XBMC.MusicPlayerSampleRate= stream["Sample_rate"]
        XBMC.MusicPlayerBitRate= stream["Bitrate"]

    @classmethod
    def GetItem(c,playerid,properties=[]):
        s= AudioLibrary.songs[ c.itemid ]
        r= subdict( s, properties)
        return r
    @classmethod
    def GetProperties(c,playerid,properties):
        return subdict( vlc.status(), properties)

class VideoLibrary(RPC):
    musicvideos= [ { "musicvideoid":1, "album":"emerald" } ]
    @classmethod
    def GetMovies(c,**p):
        return [ { "title": "indianajones", "file":"indiana.Avi" } ]
    @classmethod
    def GetTVShows(c,**p):
        return [ { "title": "seinfield", "file":"seinfield.Avi" } ]
    @classmethod
    def GetMusicVideos(c,properties,limits,sort=False):
        return c.GetList("musicvideos",properties,limits)

    
class AudioLibrary(RPC):
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
        return {}
    @classmethod
    def GetDirectory(c,**p):
        return {}
    
def handleudp():
    event.handleudp(globals(), locals())

def execute(j):
    c,m= j["method"].split(".")
    C= globals()[c]
    if j.has_key("params"):
        r=getattr(C,m)(**j["params"])
        print c,m,j["params"],":",r,C
        return r
    else:
        r= getattr(C,m)()
        print c,m,":",r,C
        return r

