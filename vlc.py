import requests

class vlc:
    log= open("log/vlc.txt","w")
    root= "http://:vlc@127.0.0.1:10000/requests/"
    @classmethod
    def command(c, cc,**kwargs):
        args=[cc]
        for t in kwargs.items():
            args.append(t[0]+"="+str(t[1]))
        req= c.root + "status.json?command=" + "&".join(args)
        print req
        r= requests.get(req)
       # print r.text
        return r.json()
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

def youtube(f):
    print "trying youtube loader",unquote(f)
    if not youtube in unquote(f): return None
    print "ok thi si syoutube"
    if "video_id=" in f: sep= "video_id="
    if "videoid=" in f: sep= "videoid="
    id= f.split(sep)[1]
    return "http://youtube.com/watch?v="+id

