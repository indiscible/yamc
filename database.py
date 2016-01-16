from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3._util import ID3NoHeaderError
from os import path,mkdir,walk
from json import dump,load
from hashlib import sha1
import sys

src= sys.argv[1] if len(sys.argv)>1 else "C:\\Music"
print sys.argv,src
dst= "database"
thumbs= "image"
if not path.exists(thumbs): mkdir(thumbs)


def Thumbnail(img):
    if img:
        h= sha1( img.data ).hexdigest();
        with open( path.join(thumbs,h),"wb") as out:
            out.write(img.data)
        return h
    return ""

def Song(songid=None, album=None, artist=None, **o):
    f= o["file"]
    songid= songid or SongId.get(f)
    if songid: return songs[ songid-1 ]
    songid= len(songs)+1
    o["songid"]= songid
    artistid= ArtistId[artist]
    a= Album( title= album )
    if not a.has_key("artistid"):
        a["artistid"]=[]
    if not artistid in a["artistid"]:
        a["artistid"].append(artistid)
    o["albumid"]= a["albumid"]
    o["artistid"]= [artistid]
    SongId[f]= songid
    songs.append(o)
    dumpdb()
    return o

def Artist(artistid=None, **a):
    name= a["artist"]
    artistid= artistid or ArtistId.get(name)
    if artistid:
        if len(a):
            artists[ artistid-1 ].update(a)
            dumpdb()
        return artists[ artistid-1 ]
    artistid= len(artists)+1
    a["artistid"]= artistid
    ArtistId[name]= artistid
    artists.append(a)
    return a

def Album(albumid=None,**a):
    t= a["title"]
    albumid= albumid or AlbumId.get(t)
    if albumid:
        if len(a):
            albums[albumid-1].update(a)
            dumpdb()
        return albums[albumid-1]
    albumid= len(albums)+1
    a["albumid"]= albumid
    AlbumId[t]=albumid
    albums.append(a)
    dumpdb()
    return a

def Genre(genreid=None, title=None):
    genreid= genreid or GenreId.get(title)
    if genreid: return genres[ genreid - 1 ]
    genreid= len(genres)+1
    GenreId[title]= genreid
    g= { "title":title, "genreid": genreid } 
    genres.append(g)
    dumpdb()
    return g


def Select(t,p,l):
    v= globals()[t]
    print len(v)
    r= [ { k:r[k] for k in p if r.has_key(k) }
         for r in v[ l["start"]:l["end"] ] ]
    l["total"]= len(v)
    l["end"]= len(r)
    return { t: r, "limits":l }

def dumptable(t,n,**kw):
    dump( t, open(path.join(dst,n),"w"),
               default= lambda o: o.__dict__, **kw)
def opendir(d):
    for (ppath,ndir,nfile) in walk(d):
        for name in nfile:
            print name
            print Mp3.Open( path.join(ppath,name) )
def dumpdb():    
    dumptable( songs, "songs.json")
    dumptable( artists, "artists.json" )
    dumptable( albums, "albums.json" )
    dumptable( genres, "genres.json")
    
def show(o):
    for k in dir(o):
        if k[0]=='_': continue
        print k,":",getattr(o,k)

class Mp3:
    @classmethod
    def Open(c,f):
        try: i= EasyID3(f)
        except ID3NoHeaderError: return None
        t= Thumbnail(i._EasyID3__id3.get("APIC:"))
        j= { k:v[0] for k,v in i.items() }
        c.Artist(thumbnail=t,**j)
        c.Album(thumbnail=t,**j)
        c.Genre(**j)
        try:
            ff= f.encode("utf_8")
        except UnicodeDecodeError:
            ff= f.decode("latin_1").encode("utf_8")
        return c.Song(file=ff,thumbnail=t, **j)

    @classmethod 
    def Artist(c,artist="Unknown Artist",**a):
        return Artist(artist=artist, thumbnail= a["thumbnail"] )

    @classmethod 
    def Album(c,album="Unknown Album", artist="Unknown Artist", **a):
        return Album(title=album, displayartist=artist,
                     thumbnail=a["thumbnail"] )
 
    @classmethod 
    def Genre(c,genre=None,**o):
        if not genre: return None
        return Genre(title=genre) 
        
    @classmethod 
    def Song(c, genre="", date="1976", tracknumber="0/0", length="0",
         discnumber="0/0", album="Unknown Album", artist="Unknown Artist",
             **s ):
        return Song(
            file= s.get("file"),
            title= s.get("title"),
            album= album,
            artist= artist,
            thumbnail= s["thumbnail"],
            genre= genre if type(genre)==list else [genre],
            year= date[:4],
            track= int(tracknumber.split("/")[0]),
            duration= int(length)//1000,
            disc= int(discnumber.split("/")[0]))



if not path.exists(dst):
    mkdir(dst)
    songs= []
    SongId= {}
    albums= []
    AlbumId= {}
    artists= []
    ArtistId= {}
    genres= []
    GenreId= {}
    opendir(src)
    dumpdb()
else:
    songs= load( open("database/songs.json","r") )
    SongId= { s["file"]:s["songid"] for s in songs }
    artists= load( open("database/artists.json", "r") )
    ArtistId= { a["artist"]:a["artistid"] for a in artists }
    albums= load( open("database/albums.json","r") )
    AlbumId= { a["title"]:a["albumid"] for a in albums }
    genres= load( open("database/genres.json", "r") )
    GenreId= { g["title"]:g["genreid"] for g in genres }
    
