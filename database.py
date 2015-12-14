from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from os import path,mkdir,walk
from json import dump
from hashlib import sha1

src= "/mnt/samsung/music"
dst= "database"
thumbs= "image"

dumpdb= True

if not path.exists(dst): mkdir(dst)
if not path.exists(dst): mkdir(thumbs)
    
songs=[]
for (ppath,ndir,nfile) in walk(src):
    for name in nfile:
        songs.append(path.join(ppath,name))

open(path.join(dst,"songs.txt"),"w").writelines(songs)

def Thumbnail(img):
    if img:
        h= sha1( img.data ).hexdigest();
        with open( path.join(thumbs,h),"wb") as out:
            out.write(img.data)
        return h
    return ""

songs=[]
def Song(f):
    if path.splitext(f)[1]!='.mp3':
        return
    print f
    i= EasyID3(f)
    d3= i._EasyID3__id3
    s={
        "title": i["title"][0],
        "artist": "",
        "year": 0,
        "album": 0,
        "track": 0,
        "musicbrainztrackid": "" ,
#i["musicbrainz_trackid"][0],
        "musicbrainzartistid": "",
#i["musicbrainz_artistid"][0],
        "musicbrainzalbumid": "" ,
#i["musicbrainz_albumid"][0],
        "musicbrainzalbumartistid": "",
#i["musicbrainz_albumartistid"][0],
        "file": f,
        "disc": 0,
        "thumbnail":"",
        "rating":0,
        "duration":0
        }
    if i.has_key('length'):
        s["duration"]= int(i["length"][0])/1000
    print s["duration"]
    if d3.has_key('APIC:'):
        s["thumbnail"]= Thumbnail(d3["APIC:"])
    if i.has_key("date"):
        s["year"]= int(i["date"][0][:4])
    if i.has_key("discnumber"):
        s["disc"]= int(i["discnumber"][0].split("/")[0])
    if i.has_key("album"):
        s["album"]= i["album"][0]
    if i.has_key("tracknumber"):
        s["track"]=int(i["tracknumber"][0].split("/")[0])
    if i.has_key("artist"):
        s["artist"]=i["artist"][0]
    if i.has_key("genre"):
        s["genre"]=[ Genre( i["genre"][0] ) ]
        print i["genre"]
    s["songid"]= len(songs)+1
    s["artistid"]= Artist(s)
    s["albumartistid"]= [s["artistid"]]
    s["albumid"]= Album(s)
    
    songs.append(s)
    
artistid={}
artists=[]
def Artist(s):
    global artistsid
    if artistid.has_key( s["artist"] ):
        return artistid[ s["artist"] ]
    a= {
        "artist": s["artist"],
        "description": s["artist"],
        "thumbnail": s["thumbnail"]
        } 
    if s.has_key("genre"): a["genre"]= s["genre"]
    newid= len(artists)+1
    a["artistid"]=newid
    artists.append(a)
    artistid[ s["artist"] ]= newid    
    return newid

albumid={}
albums=[]
def Album(s):
    global albumid
    if albumid.has_key( s["album"] ):
        return albumid[ s["album"] ]
    a={
         "title": s["album"],
         "albumlabel": s["album"],
         "artist": s["artist"],
         "displayartist": s["artist"],
         "description": s["album"],
         "rating":0,
         "year": s["year"],
         "musicbrainzalbumid":s["musicbrainzalbumid"],
         "musicbrainzalbumartistid":s["musicbrainzalbumartistid"],
         "thumbnail": s["thumbnail"],
         "artistid": [s["artistid"]],
         "rating":0,
         }
    if s.has_key("genre"): a["genre"]= s["genre"]
    newid= len(albums)+1
    a["albumid"]=newid
    albums.append(a)
    albumid[ s["album"] ]= newid
    return newid

genreid={}
genres=[]
def Genre(g):
    if genreid.has_key(g): return g
    nid= len(genres)+1
    genres.append( { "title": g, "label":g, "genreid": nid})
    genreid[g]= nid
    return g

for (ppath,ndir,nfile) in walk(src):
    for name in nfile:
        Song( path.join(ppath,name) )
         
if dumpdb:
    dump( songs, open(path.join(dst,"songs.json"),"w"))
    dump( artists, open(path.join(dst,"artists.json"),"w"))
    dump( albums, open(path.join(dst,"albums.json"),"w"))
    dump( genres, open(path.join(dst,"genres.json"),"w"))
