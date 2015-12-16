import subprocess
import event
import json
import time
import requests
from os import path,mkdir
from urllib import unquote

if not path.exists("log"): mkdir("log")

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
    def VolumeChanged(c):
        event.post( "OnVolumeChanged", 
                    { "muted": c.muted, "volume": c.volume } )

    @classmethod
    def SetMute(c,mute):
        c.muted= not c.muted
        if c.muted:
            vlc.command("volume",val=0)
        else:
            vlc.command("volume",val=c.volume)
        c.VolumeChanged()

    @classmethod
    def SetVolume(c,val):
        c.volume=val
        vlc.command("volume",val=c.volume)
        c.VolumeChanged()
        
def Mute(): Application.SetMute("toggle")
def skipminus(): Player.Minus()
def skipplus(): Player.Plus()
def forward(): vlc.command("seek",val="+5")
def reverse(): vlc.command("seek",val="-5")
def volumeminus(): Application.SetVolume( Application.volume-16 )
def volumeplus(): Application.SetVolume( Application.volume+16 )
MusicLibrary= "Hello"
Videos="Videos"
TvShowTitles="TvShowTitles"
def ActivateWindow(w): print "ActivateWindows:", w

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
    log= open("log/vlc.txt","w")
    root= "http://:vlc@127.0.0.1:10000/requests/"
    @classmethod
    def command(c, cc,**kwargs):
        args=[cc]
        for t in kwargs.items():
            args.append(t[0]+"="+str(t[1]))
        req= c.root + "status.json?command=" + "&".join(args)
        c.log.write(req)
        c.log.write("\n")
        r= requests.get(req).json()
        c.log.write(str(r))
        c.log.write("\n")
        c.log.flush()
        return r
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
    items=[]
    node=[]
    dirty=True
    count=0
    @classmethod
    def refresh(c):
        if not c.dirty: return
        c.items=[]
        c.node=[]
        f2i={}
        pl= vlc.playlist()["children"][0]["children"]

        for s in AudioLibrary.songs: f2i[s["file"]]= s["songid"]

        for i in pl:
            uri= path.normpath(unquote(i["uri"][7:]))
            print uri
            if f2i.has_key(uri):
                c.node.append( int(i["id"]) )
                c.items.append( AudioLibrary.songs[ f2i[uri]-1 ] )
        c.dirty= False
        print c.node

    @classmethod
    def GetItems(c,playlistid, limits, properties=[]):
        c.refresh()
        return c.GetList("items",properties,limits)
        
    @classmethod
    def Clear(c,playlistid):
        vlc.command("pl_empty")
        c.dirty= True
        c.count=0
        return "OK"

    @classmethod
    def Add(c,playlistid,item):
        if "file" in item:
            id= item["file"].split("video_id")[1]
            vlc.command("in_play",input="http://youtube.com/watch?v="+id)
        else:
            print item
            sid= item["songid"]
            vlc.command("in_enqueue",
                        input= AudioLibrary.songs[sid-1]["file"])
            event.post( "Playlist.OnAdd",
                        { "items": { "id": sid, "type":"song" },
                          "playlistid": playlistid,
                          "position": c.count } )
            c.count=c.count+1
            c.dirty= True
        return "OK"

class Player(RPC):
    playerid=0
    type="audio"
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
    duration=0
    item={}
    @classmethod
    def OnPlay(c):
        event.post( "Player.OnPlay", 
                    { "items": { "id": c.item["songid"], "type":"song" },
                      "player": { "playerid": c.playerid, "speed":c.speed } } )

    @classmethod
    def Plus(c):
        vlc.command("pl_next")
        c.position= (c.position+1)%len(Playlist.items)
        c.OnPlay()

    @classmethod
    def Minus(c):
        vlc.command("pl_previous")
        c.position= (c.position-1)%len(Playlist.items)
        c.OnPlay()
        
    @classmethod
    def GetActivePlayers(c):
        print c.playerid, c.type
        return [{"playerid":c.playerid, "type":c.type}]
    @classmethod
    def Open(c,item):
        if item.has_key("playlistid"):
            Playlist.refresh()
            print item
            c.position= item["position"]
            c.item= Playlist.items[ c.position ]
            print "playlist:", c.item
            r= vlc.command("pl_play",id=Playlist.node[ c.position ])
        else:
            print "play songd: ", item
            c.item= AudioLibrary.songs[ item["songid"]-1 ]
            r= vlc.command("in_play", input= c.item["file"])
            Playlist.dirty= True
        c.type= "audio"
        c.playerid=0
        c.OnPlay()
        try:
            stream= r["information"]["category"]["Stream 0"]
            XBMC.MusicPlayerCodec= stream["Codec"]
            XBMC.MusicPlayerSampleRate= stream["Sample_rate"]
            XBMC.MusicPlayerBitRate= stream["Bitrate"]
        except KeyError as e:
            print "KeyError:", e, r

    @classmethod
    def PlayPause(c,playerid,play):
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
    def SetSpeed(c,playerid,speed):
        if speed==1:
            vlc.command("pl_play")

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
        vlc.command("seek",val=int(value*c.duration//100))
        r= c.Get(["totaltime","percentage","time"] )
        print r
        return r

    @classmethod
    def GetItem(c,playerid,properties=[]):
        r= subdict( c.item, properties )
        print c.item
        return { "item":r }

    @classmethod
    def GetProperties(c,playerid,properties):
        s= vlc.status();
        Playlist.refresh()
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
        n=Playlist.node
        print c.position
        if s.has_key("currentplid"):
            id= s["currentplid"]
            if id in n:
                c.position= n.index(id)
        if c.position<len(Playlist.items):        
            c.item= Playlist.items[c.position]
        if s["state"]=="stopped":
            c.speed=0
        elif s["state"]=="playing":
            c.speed=1
#        print c.Get(properties)
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
    genres= json.load( open("database/genres.json", "r") )

    @classmethod
    def GetArtists(c,limits,properties=[]):
        properties.append("artistid")
        properties.append("artist")
        properties.append("genre")
        return c.GetList("artists",set(properties),limits)

    @classmethod
    def GetGenres(c,limits,properties=[]):
        properties.append("genreid")
        return c.GetList("genres",set(properties),limits)

    @classmethod
    def GetAlbums(c,limits,properties=[]):
        properties.append("albumid")
        properties=["albumid","artistid","albumlabel","title","thumbnail","genre"]
        return c.GetList("albums",set(properties),limits)

    @classmethod
    def GetSongs(c,limits, properties=[]):
        properties=["songid","title","track","rating","duration","albumid","genre"]
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
    print c,m
    try:
        if j.has_key("params"):
#            print c,m,j["params"]
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
