import subprocess
import event
import plugin
import external
import json
import time
import requests
from playlist import Playlist
from audiolibrary import AudioLibrary
import vlc

from rpc import RPC
from os import path,mkdir
from urllib import unquote,quote

if not path.exists("log"): mkdir("log")
    
def subdict(d,p):
    return { k:d[k] for k in p if d.has_key(k) }

class JSONRPC(RPC):
    version= { "major": 6, "minor": 25, "patch": 2}
    @staticmethod
    def Ping():
        return 'pong'
    @classmethod
    def Version(c):
        return c.Get(["version"])
    
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
        event.post().OnVolumeChanged(muted=c.muted, volume=c.volume)

    @classmethod
    def SetMute(c,mute):
        c.muted= not c.muted
        if c.muted:
            vlc.command("volume",val=0)
        else:
            vlc.command("volume",val=256*(c.volume/100.0))
        c.VolumeChanged()
        return "OK"

    @classmethod
    def SetVolume(c,volume):
        c.volume=volume
        vlc.command("volume",val=256*(c.volume/100.0))
        c.VolumeChanged()
        
def Mute(): Application.SetMute("toggle")
def skipminus(): Player.Minus()
def skipplus(): Player.Plus()
def forward(): vlc.command("seek",val="+5%")
def reverse(): vlc.command("seek",val="-5%")
def volumeminus(): Application.SetVolume( Application.volume-16 )
def volumeplus(): Application.SetVolume( Application.volume+16 )

#MusicLibrary= "Hello"
#Videos="Videos"
#TvShowTitles="TvShowTitles"
#def ActivateWindow(w): print "ActivateWindows:", w

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

def time2seconds(ss):
    return ss["hours"]*3600 + ss["minutes"]*60 + ss["seconds"]
        
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
    def OnPlay(c,songid=None,**item):
        item[ "type" ]="song"
        if songid!=None: item["id"]=songid
        event.post().Player.OnPlay( 
            items= item,
            player= { "playerid": c.playerid, "speed":c.speed } )

        
    @classmethod
    def Plus(c):
        vlc.command("pl_next")
        c.position= Playlist.position( **vlc.status() )
        print "plus:", c.position
        c.OnPlay( **Playlist.items[c.position] )
        Playlist.dirty= True
  
    @classmethod
    def Minus(c):
        vlc.command("pl_previous")
        c.position= Playlist.position( **vlc.status)
        c.OnPlay( **Playlist.items[c.position] )
        Playlist.dirty= True
        
    @classmethod
    def GetActivePlayers(c):
        print c.playerid, c.type
        return [{"playerid":c.playerid, "type":c.type}]

    @classmethod
    def Open(c,item):
        print item
        c.item= Playlist.Open( **item )
        if not c.item: raise Exception, 'Cannot open'+ str(item)
        c.type= "audio"
        c.playerid=0
        c.OnPlay(**c.item)
        
    @classmethod
    def PlayPause(c,playerid,**k):
        if k.has_key("play"):
            if k["play"] and c.speed==1: return "OK"
            if not k["play"] and c.speed==0: return "OK"

        s=vlc.command("pl_pause")
        if s["state"]=="paused":
            c.speed= 0
        elif s["state"]=="playing":
            c.speed= 1
        c.OnPlay()
        return "OK"

    @classmethod
    def Stop(c,playerid):
        vlc.command("pl_stop")
        return "OK"

    @classmethod
    def SetSpeed(c,playerid,speed):
        if speed==1:
            vlc.command("pl_play")

    @classmethod
    def GoTo(c,playerid, to ):
        vlc.command("pl_play",id=Playlist.getnodes()[to] )
        c.position= to
        return "OK"
        
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
        if type(value)==dict:
            pos= time2seconds(value)
        elif type(value)==float:
            pos= value*c.duration//100
        print value,pos
        vlc.command("seek",val=pos)
        r= c.Get(["totaltime","percentage","time"] )
        print r
        return r

    @classmethod
    def GetItem(c,playerid,properties=[]):
        r= subdict( c.item, properties )
#        print c.item
        return { "item":r }

    @classmethod
    def GetProperties(c,playerid,properties):
        s= vlc.status();
        try:
            stream= s["information"]["category"]["Stream 0"]
            XBMC.MusicPlayerCodec= stream["Codec"]
            XBMC.MusicPlayerSampleRate= stream["Sample_rate"]
            XBMC.MusicPlayerBitRate= stream["Bitrate"]
        except KeyError as e:
            print "KeyError:", e

        if s["loop"]:
            c.repeat="on" 
        elif s["repeat"]:
            c.repeat="all"
        else:
            c.repeat="off"
        c.shuffled= s["random"]
        c.duration= s["length"]
        c.percentage=s["position"] 
        c.time= seconds2time(s["position"]*s["length"])
        c.totaltime= seconds2time(s["length"])
        c.volume= s["volume"]/255.0
        c.position= Playlist.position(**s)
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
    if j.has_key("params"):
        #            print c,m,j["params"]
        r=getattr(C,m)(**j["params"])
#            print c,m,j["params"],":",r
        return r
    else:
        r= getattr(C,m)()
#            print c,m,":",r
        return r


