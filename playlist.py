from rpc import RPC
import vlc
import plugin
import yamc
from urllib import quote

class Playlist(RPC):
    items=[]
    nodes=[]
    dirty=True
    
    @staticmethod
    def GetPlaylists():
        return { "items":{ "playlistid":0, "type":"audio" } }
    
    @classmethod
    def GetItems(c,playlistid, limits, properties=[]):
        return c.GetList("items",properties,limits)

    @classmethod
    def Clear(c,playlistid):
        vlc.command("pl_empty")
        c.items=[]
        c.dirty= True
        return "OK"
    
    @classmethod
    def Add(c,playlistid,item):
        items= plugin.get( **item ) or \
              yamc.AudioLibrary.Get( **item )
        if not items: return "Not found"

        for i in items:
            print i 
            i["type"]="song"        
            vlc.command("in_enqueue", input= quote(i["file"],safe='') )
            c.items.append( i )
            yamc.event.post().Playlist.OnAdd(
                i,
                playlistid= playlistid,
                position= len(c.items)  )
        c.dirty= True
        return "OK"

    @classmethod
    def Open(c,playlistid=None, position=None, **o):
        if playlistid==None or position==None:
            position= len(c.items)
            if c.Add(0,o)!="OK":
                print "cannot add item:", o
                return {}
        
        print "playlist one position:", position
        print "nodes:", c.getnodes()
        vlc.command("pl_play", id= c.getnodes()[position])
        return c.items[position]
        
    @classmethod
    def getnodes(c):
        if len(c.nodes)!=len(c.items): c.dirty= True
        if not c.dirty: return c.nodes
        pl= vlc.playlist()
        c.nodes= [ int(i["id"]) for i in pl ]
        if len(c.nodes)>len(c.items):
            c.items= [
                { 'title': i["name"], 'file': i["uri"] }
                for i in pl ]
        c.dirty= False
        return c.nodes

    @classmethod
    def position(c,currentplid=None,**o):
        print "currentplid:", currentplid
        print c.getnodes()
        if currentplid!=None:
            if currentplid in c.nodes:
                return c.getnodes().index(currentplid)
        else:
            pl= vlc.playlist()
            for i in pl:
                if i.get("current"):
                    return pl.index(i)
        c.dirty= True
        return 0


