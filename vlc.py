import requests

log= open("log/vlc.txt","w")
root= "http://:vlc@127.0.0.1:10000/requests/"

def command(cc,**kwargs):
    args=[cc]
    for t in kwargs.items():
        args.append(t[0]+"="+str(t[1]))
    req= root + "status.json?command=" + "&".join(args)
    print req
    r= requests.get(req)
    # print r.text
    return r.json()

def status():
    return requests.get( root + "status.json" ).json()

def playlist():
    r= requests.get( root + "playlist.json" ).json()
    try:
        return r["children"][0]["children"]
    except KeyError:
        print "Error getting playlist from vlc"
        print r
        return []
        
def audiostream(ss):
    for s in ss.values():
        if s["Type"]=="Audio":
            return s
    return None


