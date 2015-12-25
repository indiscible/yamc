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
        item= plugin.get( **item ) or \
              yamc.AudioLibrary.Get( **item )
        if not item: return "Not found"
        print item
        item["type"]="song"        
        vlc.command("in_enqueue", input= quote( item["file"] ) )
        c.items.append( item )
        yamc.event.post().Playlist.OnAdd(
            item,
            playlistid= playlistid,
            position= len(c.items)  )
        c.dirty= True
        return "OK"

    @classmethod
    def Open(c,playlistid=None, position=None, **o):
        if playlistid==None or position==None:
            if c.Add(0,o)!="OK":
                print "cannot add item:", o
                return {}
            position= len(c.items)-1
        print "playlist opne position:", position
        print "nodes:", c.getnodes()
        vlc.command("pl_play", id= c.getnodes()[position])
        return c.items[position]
        
    @classmethod
    def getnodes(c):
        print "getnodes"
        if not c.dirty: return c.nodes
        c.nodes= [ int(i["id"]) for i in vlc.playlist() ]
        c.dirty= False
        return c.nodes

    @classmethod
    def position(c,currentplid=None,**o):
        if currentplid:
            if currentplid in c.nodes:
                return c.nodes.index(currentplid)
        else:
            pl= vlc.playlist()
            for i in pl:
                if i.get("current"):
                    return pl.index(i)
        return 0


