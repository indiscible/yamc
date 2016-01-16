import database
import vlc
from urllib import unquote,quote
import requests
import os
import json
import re
from urlparse import urlparse,parse_qs

def Thumbnail(url):
    if not url: return ""
    u= urlparse(url)
    q= os.path.normpath(u.path[1:])
    p= os.path.join("image",q)
    if not os.path.exists(p):
        d= os.path.split(p)[0]
        if not os.path.exists(d): os.makedirs(d)
        open(p,'wb').write( requests.get(url).content )
    return q

class youtube:
    root='http://youtube.com/'
    key= "AIzaSyBsU-XLWFjoSTf5Z42Yp5LGnV9-5JdWg6g"
    api= "https://www.googleapis.com/youtube/v3/"
    @classmethod
    def Open(c,f):
        u= urlparse(f)
        print u
        if not "youtube" in u.netloc: return None
        q= { k:v[0] for k,v in parse_qs(u.query).items() }
        return c.Playlist(**q) or [c.Video(**q)]
        
    @staticmethod
    def to_seconds(t):
        m= re.match(r"PT((\d*)H)?((\d*)M)?(\d*)S",t)
        if not m:
            print "no duration:", t
            return 0
        hh,h, mm, m,s= m.groups()
        h= h or 0
        m= m or 0
        return int(h)*3600+int(m)*60+int(s)
    
    @classmethod
    def Video(c,id=None, v= None, videoid=None, video_id=None, album=None, track=0, **o):
        id= id or v or videoid or video_id
        if not id: return None
        j= c.resolve(
                    "videos",
                    id= id,
                    part="snippet,contentDetails")["items"]
        if len(j)==0: return None
        j= j[0]
        snippet= j["snippet"]
        details= j["contentDetails"]
        artist= c.Artist(**snippet)
        album= album or c.Album(**snippet)
        print snippet["thumbnails"]
        return database.Song(
            title= snippet["title"],
            artist= artist["artist"],
            duration= c.to_seconds( details["duration"] ),
            thumbnail= Thumbnail( snippet["thumbnails"]["default"]["url"] ),
            album= album["title"],
            track= track,
            file= c.root + "watch?v=" + id )
        
    @classmethod
    def Album(c, title, thumbnails, **o):
        return database.Album(
            title= title,
            thumbnail= Thumbnail( thumbnails["medium"]["url"]) )
                               
    @classmethod
    def Artist(c, channelId=None, **o):
        snippet= c.resolve("channels",
                           part="snippet",
                           id=channelId)["items"][0]["snippet"]
        return database.Artist( artist= snippet["title"],
                                thumbnail= Thumbnail(snippet["thumbnails"]["medium"]["url"]) )
    
    @classmethod
    def Playlist(c,playlist_id=None,list=None,**o):
        id= playlist_id or list
        if not id: return None
        j= c.resolve( "playlists", 
                            id= id,
                            part="snippet")
        if j.has_key("items"): j= j["items"][0]
        snippet= j["snippet"]
        print snippet
        artist= c.Artist( **snippet )
        album= c.Album( **snippet )
        items= c.resolve( "playlistItems",
                          playlistId= id,
                          part="snippet",
                          maxResult=50)["items"]
        #genre= database.Genre(genre=j["genre"])
        return [ c.Video(id=x["snippet"]["resourceId"]["videoId"],
                         album= album)
                 for x in items ]

    @classmethod
    def resolve(c,w,refresh=False,**o):
        if len(o)==0: return None
        print o
        r= o.get("orUsername") or o.get("playlistId") or o.get("id")
        p= os.path.join("youtube.com",w,r)
        print o,"=>", p
        if (not refresh) and os.path.exists(p): return json.load(open(p))
        query= "?" + "&".join( [ str(k)+"="+str(v) for k,v in o.items() ] )
        print query
        j= requests.get(c.api+w+query + "&key="+c.key).json()
        dir= os.path.split(p)[0] 
        if not os.path.exists(dir): os.makedirs(dir)
        json.dump( j, open(p,"wb"), indent=2 )
        return j


def get(file=None,**o):
    if not file: return None
    return youtube.Open(file) or soundcloud.Open(file)

class soundcloud:
    root="https://api.soundcloud.com/"
    key="client_id=d286f9f11bac3d365b66cf9092705075"
    
    @classmethod
    def Open(c,f):
        u= urlparse(f)
        if not "soundcloud" in u.netloc: return None
        url= unquote(u.query)
        if "https" in url: url= url.split("https://")[1]
        else: url= url.split("http://")[1]
        j= c.resolve(url)
        return c.Set(**j) or [ c.Song(**j) ]
        
    @classmethod
    def Song(c,track=0,album=None, **s):
        artist= database.Artist(artist=s["user"]["username"],
                                thumbnail=Thumbnail(s["user"]["avatar_url"]))
        album= album or database.Album(title=s["title"],
                                       displayartist=artist["artist"],
                                       thumbnail=Thumbnail(s["artwork_url"]))["title"] 
        return database.Song(
            file= s["permalink_url"],
            title= s["title"],
            album= album, 
            artist= artist["artist"],
            duration= int(s["duration"])//1000,
            thumbnail= Thumbnail( s["artwork_url"] ),
            genre=s["genre"],
            track= track);
        
    @classmethod
    def Set(c,**s):
        if not "tracks" in s: return None
        artist= database.Artist(artist=s["user"]["username"],
                                thumbnail=Thumbnail(s["user"]["avatar_url"]))
        album= database.Album(title=s["title"],
                              displayartist=artist["artist"],
                              thumbnail= Thumbnail(s["artwork_url"]) )
        genre= database.Genre(title=s["genre"])
        tracks= s["tracks"]
        return [ c.Song(album=album["title"],track= tracks.index(t),**t)
                 for t in tracks ]

    @classmethod
    def resolve(c,url):
        try:
            return json.load(open(url))
        except (IOError,ValueError):
            r= requests.get(c.root+"resolve.json?url=https://"+url+"&"+c.key).json()
            dir=  os.path.split(url)[0] 
            if not os.path.exists(dir): os.makedirs(dir)
            json.dump( r, open(url,"wb"), indent=2 )
            return r

#print youtube.open('plugin://plugin.video.youtube/play/?playlist_id=PLEmq2-8H-ixYSptqVbvYmuFougQ-K2tN1&order=default')
#print soundcloud.Open( 'plugin://plugin.audio.soundcloud/play/?url=https%3A%2F%2Fsoundcloud.com%2Fjorge-aboumrad-vega%2Fsets%2Fdreamon' )
