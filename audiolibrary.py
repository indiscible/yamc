from rpc import RPC
import plugin
import json
import database

class AudioLibrary(RPC):
    @classmethod 
    def Get(c,songid=None,albumid=None,**o):
        if songid: return [database.songs[ songid-1 ]]
        if albumid: return [
                s for s in database.songs if s["albumid"]==albumid ]
        return None

    @classmethod
    def GetArtists(c,limits,properties=[]):
        properties.append("artistid")
        properties.append("artist")
        properties.append("genre")
        return database.Select("artists",set(properties),limits)

    @classmethod
    def GetGenres(c,limits,properties=[]):
        properties.append("genreid")
        return database.Select("genres",set(properties),limits)

    @classmethod
    def GetAlbums(c,limits,properties=[]):
        properties.append("albumid")
        properties=["albumid","artistid","albumlabel","title","thumbnail","genre"]
        return database.Select("albums",set(properties),limits)

    @classmethod
    def GetSongs(c,limits, properties=[]):
        properties=["songid","title","track","rating","duration","albumid","genre","artistid"]
        return database.Select("songs",set(properties),limits)



