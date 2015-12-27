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
    print p
    if not os.path.exists(p):
        d= os.path.split(p)[0]
        print d
        if not os.path.exists(d): os.makedirs(d)
        open(p,'wb').write( requests.get(url).content )
    return q
    
class youtube:
    root='http://youtube.com/'
    @classmethod
    def open(c,f):
        u= urlparse(f)
        if not "youtube" in u.netloc: return None
        q= { k:v[0] for k,v in parse_qs(u.query).items() }
        print q
        return c.list(**q) or [c.video(**q)]
        
    @classmethod
    def video(c,title=None,
              video_id=None, videoid=None, encrypted_id=None, v=None,
              author=None, length_seconds=0, thumbnail=None,
              **o):
        id= video_id or videoid or v or encrypted_id
        name= title or id
        if not id: return None
        return { "title": title or id,
                 "file": c.root + "watch?v=" + id,
                 "artist": author,
                 "duration": int(length_seconds),
                 "thumbnail": Thumbnail(thumbnail) }
        
    @classmethod
    def list(c,playlist_id=None,**o):
        if not playlist_id: return None
        p= os.path.join("youtube.com","list",str(playlist_id))
        if os.path.exists(p):
            j= json.load( open(p) )
        else:
            req='list_ajax?action_get_list=1&style=json&list='
            print c.root+req+str(playlist_id)
            j= requests.get(c.root+req+str(playlist_id))
            print j.text
            j= j.json()
            d= os.path.split(p)[0] 
            if not os.path.exists(d): os.makedirs(d)
            json.dump( j, open(p,"w"), indent=2 )
        return [
            c.video(**x)
            for x in j["video"] ]

def get(file=None,**o):
    if not file: return None
    return youtube.open(file) or soundcloud.open(file)

class soundcloud:
    root="https://api.soundcloud.com/"
    key="client_id=d286f9f11bac3d365b66cf9092705075"
    
    @classmethod
    def open(c,f):
        u= urlparse(f)
        if not "soundcloud" in u.netloc: return None
        url= unquote(u.query).split("https://")[1]
        return c.sets(url) or [c.song(url)]

    @classmethod
    def song(c,url,title=None):
        title=title or os.path.split(url)[1]
        return { "name":  title,
                 "file": "https://"+url }
       
    @classmethod
    def sets(c,url):
        if not "sets" in url: return None
        j= c.resolve(url)
        return [ c.song(t["permalink_url"][7:],title=t["title"])
                 for t in j["tracks"] ]

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
