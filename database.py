from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from os import path,mkdir,walk
from json import dump
from hashlib import sha1

print "database construstion"
src= "c:\\Music"
dst= "database"
thumbs= "image"

dumpdb= True

if not path.exists(dst): mkdir(dst)
if not path.exists(thumbs): mkdir(thumbs)
    
def Thumbnail(img):
    if img:
        h= sha1( img.data ).hexdigest();
        with open( path.join(thumbs,h),"wb") as out:
            out.write(img.data)
        return h
    return ""

songs=[]
class Song:
    def __init__( s, file, thumb,
          title="", artist="", album="", 
          musicbrainz_trackid="", musicbrainz_albumid="",
          musicbrainz_artistid="", musicbrainz_albumartistid="",
          date="1976", tracknumber="1/1", performer="", 
          length="0", discnumber="1/1", genre="",**o):
        s.file= file
        s.title= title
        s.artist= artist
        s.album= album
        s.genre= genre
        s.musicbrainztrackid= musicbrainz_trackid
        s.musicbrainzalbumid= musicbrainz_albumid
        s.musicbrainzalbumartistid= musicbrainz_albumartistid
        s.year= date[:4]
        s.track= int(tracknumber.split("/")[0])
        s.albumartist= performer
        s.duration= int(length)//1000
        s.disc= int(discnumber.split("/")[0])
        s.thumbnail= thumb
        s.songid= len(songs)+1  

artists=[]
class Artist:
    def __init__(s, thumb, genre="", description="", 
                 musicbrainz_artistid="", artist="", **o):
        s.genre=genre
        s.description= description
        s.musicbrainzartistid= musicbrainz_artistid
        s.artist= artist
        s.thumbnail= thumb
        s.artistid= len(artists)+1

albums=[]
class Album:
    def __init__(s, thumbnail, 
                 album="", albumlabel="", artist="", displayartist="",
                 description="", date="1976", performer="", genre=[""],
                 musicbrainz_albumid="", musicbrainz_albumartistid="", **o ):
        s.title= album
        s.albumlabel= album
        s.artist= artist
        s.albumartist= performer
        s.displayartist= artist
        s.year= date[:4]
        s.genre= genre
        s.musicbrainzalbumid= musicbrainz_albumid
        s.musicbrainzalbumartistid= musicbrainz_albumartistid
        s.thumbnail= thumbnail
        s.albumid= len(albums)+1

genres=[]
class Genre:
    def __init__(s,g):
        s.title= g
        s.label= g
        s.genreid= len(genres)+1

artistid={}
albumid={}
genreid={}

def show(o):
    for k in dir(o):
        if k[0]=='_': continue
        print k,":",getattr(o,k)

def update(t,k,e):
    if not t[0].has_key(k):
        t[1].append( e )
        t[0][k]= len(t[1])
    return t[0][k]

for (ppath,ndir,nfile) in walk(src):
    for name in nfile:
        print name
        f= path.join(ppath,name)
        i= EasyID3(f)
        t= Thumbnail(i._EasyID3__id3.get("APIC:"))
        j= { k:v[0] for k,v in i.items() }
        s= Song( f, t, **j )
        s.artistid= update( (artistid,artists), s.artist, Artist(t,**j) )
        s.albumid= update( (albumid,albums), s.album, Album(t,**j) )
        update( (genreid,genres), s.genre, Genre(s.genre) )
        albums[s.albumid-1].artistid=[ s.artistid ]
        songs.append( s )

def dumptable(t,n,**kw):
    dump( t, open(path.join(dst,n),"w"),
               default= lambda o: o.__dict__, **kw)
if dumpdb:
    dumptable( songs, "songs.json", encoding='latin-1')
    dumptable( artists, "artists.json" )
    dumptable( albums, "albums.json" )
    dumptable( genres, "genres.json")

