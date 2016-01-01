import database
import vlc
from urllib import unquote,quote
import requests
import os
import json
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
    @classmethod
    def Open(c,f):
        u= urlparse(f)
        if not "youtube" in u.netloc: return None
        q= { k:v[0] for k,v in parse_qs(u.query).items() }
        return c.list(**q) or [ c.video(**q) ]
        
    @classmethod
    def video(c, thumbnail=None, video_id=None, videoid=None, encrypted_id=None, v=None, length_seconds="0", author="", title=None, album=None, track=None, **o):
        id= video_id or videoid or v or encrypted_id
        if not id: return None
        artist= database.Artist(artist=author)
        return database.Song( 
            title= title or id,
            file= c.root + "watch?v=" + id,
            duration= int(length_seconds),
            thumbnail= Thumbnail(thumbnail),
            track= track or 0,
            album= album,
            artist= author )
        
    @classmethod
    def list(c,playlist_id=None,**o):
        if not playlist_id: return None
        p= os.path.join("youtube.com","list",str(playlist_id))
        if os.path.exists(p):
            j= json.load( open(p) )
        else:
            req='list_ajax?action_get_list=1&style=json&list='
            j= requests.get(c.root+req+str(playlist_id)).json()
            d= os.path.split(p)[0] 
            if not os.path.exists(d): os.makedirs(d)
            json.dump( j, open(p,"w"), indent=2 )
        print j
        #genre= database.Genre(genre=j["genre"])
        artist= database.Artist(artist= j["author"],compilationartist= True )
        album= database.Album(title= j["title"], displayartist= j["author"])
        return [ c.video(album= album["title"],**x)
                 for x in j["video"] ]

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
