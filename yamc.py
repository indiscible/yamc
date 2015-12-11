import subprocess
import event
import json
import vlc
import time
import requests

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
        print c,properties
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
            
def Mute():
    Application.muted= not Application.muted
    event.post( "OnVolumeChanged", 
                { "muted": c.muted, "volume": c.volume } )

def skipminus():
    Player.SkipMinus();

def skipplus():
    Player.SkipPlus()

MusicLibrary= "Hello"
Videos="Videos"
TvShowTitles="TvShowTitles"

def ActivateWindow(w):
    print "ActivateWindows:", w

class XBMC(RPC):
    SystemPlatformLinux= True
    SystemPlatformLinuxRaspberryPi= True
    SystemKernelVersion= "Gilles"
    SystemBuildVersion= "0.0"

def seconds2time(ss):
    h= int( ss//3600 )
    ss= ss%3600
    m= int( ss//60 )
    ss= ss%60
    s= int( ss )
    ss= ss%1
    ms= int( ss*1000)
    return { "hours": h, "minutes": m, "seconds": s, "milliseconds": ms }

class vlc:
    root= "http://:vlc@127.0.0.1:8080/requests/"
    @classmethod
    def command(c, cc,**kwargs):
        args=[cc]
        for t in kwargs.items():
            args.append(t[0]+"="+t[1])
        req= c.root + "status.json?command=" + "&".join(args)
        print req
        return requests.get(req).json()
    @classmethod
    def playlist(c):
        return requests.get( c.root + "playlist.json" ).json()

    @classmethod
    def status(c):
        return requests.get( c.root + "status.json" ).json()

    @classmethod
    def play(c,i):
        p= c.playlist()
        node= p["children"][0]["children"][i]["id"]
        return c.command("pl_play",id=node)
        
class Playlist(RPC):
    lists= json.load(open("database/lists.json","r"))
    @classmethod
    def save(c):
        with open("database/lists.json","w") as out:
            json.dump(c.lists, out)

    @classmethod
    def GetItems(c,playlistid, limits, properties=[]):
        v=[]
        if c.lists.has_key(playlistid):
            v= c.lists[playlistid]
        return { "items": v, "limits":{"total":len(v)} }
    @classmethod
    def Clear(c,playlistid):
        c.lists[playlistid]= []
        c.save()
        vlc.command("pl_empty")
    @classmethod
    def Add(c,playlistid,item):
        sid= item["songid"]
        pl= c.lists[playlistid]
        pl.append( AudioLibrary.songs[sid-1] )
        print vlc.command("in_enqueue",
             input= AudioLibrary.songs[sid-1]["file"])
        event.post( "Playlist.OnAdd",
                    { "items": { "id": sid, "type":"song" },
                      "playlistid": playlistid,
                      "position": len(pl)-1 } )
        c.save()
        return "OK"

class Player(RPC):
    playerid=0
    type=""
    audiostreams=[]
    canseek= True
    currentaudiostream={}
    currentsubtitle=None
    partymode= False
    playlistid= 0
    position= 0
    repeat= "off"
    shuffled= False
    speed= 1
    subtitleenabled= False
    subtitles=[]
    time= { "hours": 0, "minutes":0, "seconds": 0, "milliseconds":0 }
    totaltime= { "hours": 0, "minutes":0, "seconds": 0, "milliseconds":0 }
    itemid=-1
    duration=0
    @classmethod
    def GetActivePlayers(c):
        return [{"playerid":c.playerid, "type":c.type}]
    @classmethod
    def Open(c,item):
        if item.has_key("playlistid"):
            c.playlistid=item["playlistid"]
            c.position= item["position"]
            pl= Playlist.lists[c.playlistid]
            c.itemid= pl[c.position]["songid"]-1
            r= vlc.play(c.position)
        else:
            c.itemid= item["songid"]-1
            s= AudioLibrary.songs[ c.itemid ]
            r= vlc.command("in_play", input= s["file"])
        c.type= "audio"
        c.playerid=0
        event.post( "Player.OnPlay", 
                    { "items": { "id": c.itemid, "type":"song" },
                      "player": { "playerid": c.playerid, "speed":c.speed } } )
        try:
            stream= r["information"]["category"]["Stream 0"]
            XBMC.MusicPlayerCodec= stream["Codec"]
            XBMC.MusicPlayerSampleRate= stream["Sample_rate"]
            XBMC.MusicPlayerBitRate= stream["Bitrate"]
        except KeyError as e:
            print "KeyError:", e, r

    @classmethod
    def PlayPause(c,playerid):
        s=vlc.command("pl_pause")
        if s["state"]=="paused":
            c.speed= 0
        elif s["state"]=="playing":
            c.speed= 1
        return c.speed
    @classmethod
    def Stop(c,playerid):
        vlc.command("pl_stop")
    @classmethod
    def SkipPlus(c):
        vlc.command("pl_next")
    @classmethod
    def SkipMinus(c):
        vlc.command("pl_previous")
    @classmethod
    def GoTo(c,playerid, to ):
        c.Open({ "playlistid":0, "position":to })
    @classmethod
    def SetRepeat(c,playerid,repeat):
        print "repeat:", repeat
        if repeat=="one":
            vlc.command("pl_loop")
        elif repeat=="all":
            vlc.command("pl_repeat")
        c.repeat= repeat

    @classmethod
    def SetShuffle(c,playerid,shuffle):
        vlc.command("pl_random")
        return "OK"

    @classmethod
    def Seek(c,playerid,value):
        print value, c.duration
        vlc.command("seek",val=str(int(value*c.duration//100)))
        r= c.Get(["totaltime","percentage","time"] )
        print r
        return r

    @classmethod
    def GetItem(c,playerid,properties=[]):
        s= AudioLibrary.songs[ c.itemid ]
        r= subdict( s, set(properties) )
        return { "item":r }

    @classmethod
    def GetProperties(c,playerid,properties):
        s= vlc.status();
        if s["loop"]:
            c.repeat="on"
        elif s["repeat"]:
            c.repeat="all"
        else:
            c.repeat="off"
        c.duration= s["length"]
        c.percentage=s["position"] 
        c.time= seconds2time(s["position"]*s["length"])
        c.totaltime= seconds2time(s["length"])
        c.shuffled= s["random"]
        if s["state"]=="stopped":
            c.position=0
        elif s["state"]=="playing":
            c.position=1
        properties.append("type")
        return c.Get(properties)

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
    
def handleudp(s):
    event.handleudp(s,globals(), locals())

def execute(j):
    c,m= j["method"].split(".")
    C= globals()[c]
#    print c,m
    try:
        if j.has_key("params"):
            r=getattr(C,m)(**j["params"])
#            print c,m,j["params"],":",r
            return r
        else:
            r= getattr(C,m)()
#            print c,m,":",r
            return r
    except AttributeError as e:
        print e, j
    except TypeError as e:
        print e, j
