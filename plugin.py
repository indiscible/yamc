import vlc
from urllib import unquote,quote
import requests

def youtube(f):
    if not "youtube" in f: return None
    if "videoid=" in f: id= f.split("videoid=")[1]
    if "video_id=" in f: id= f.split("video_id=")[1]
    elif "watch?v=" in f: id= f.split("watch?v=")[1]
    input= 'http://youtube.com/watch?v='+id
    return { "name": id, "file":input }
    
def Open(file=None):
    if not file: return None
    item= resolve(file)
    print len(item)
    if type(item["file"])==list:
        print item["file"]
        vlc.command("pl_empty")
        for t in item["file"]:
            vlc.command("in_enqueue",input=quote(t))
        vlc.command("pl_play")
        return { "playlistid":0, "position":1 }
    else:
        vlc.command("in_play",input=quote(item["file"]))
    return item

def get(file=None,**o):
    if not file: return None
    return youtube(file) or soundcloud.open(file)

class soundcloud:
    root="https://api.soundcloud.com/"
    key="client_id=d286f9f11bac3d365b66cf9092705075"
    
    @classmethod
    def open(c,f):
        if not "soundcloud" in f: return None
        input= unquote(f).split("url=")[1]
        id= unquote(f).split("soundcloud.com")[1]
        if "sets" in input:
            return { "name": id, "file": c.set(input) }
        return { "name":id, "file":input }

    @classmethod
    def set(c,url):
        j= c.resolve(url).json()
        return [ t["permalink_url"] for t in j["tracks"] ]

    @classmethod
    def resolve(c,url):
        return requests.get(c.root+"resolve.json?url="+url+"&"+c.key)
