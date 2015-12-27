from rpc import RPC
from glob import glob
import json

print [ x["title"]
        for f in glob("youtube.com\list\*") 
        for x in json.load(open(f))["video"] ]

class AudioLibrary(RPC):
    songs= json.load( open("database/songs.json","r") )
    albums= json.load( open("database/albums.json","r") )
    artists= json.load( open("database/artists.json", "r") )
    genres= json.load( open("database/genres.json", "r") )
    
    @classmethod 
    def get(c,songid=None,**o):
        if not songid: return none
        return c.songs[ songid-1 ]

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

