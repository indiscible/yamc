from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from os import walk
from json import dump
from hashlib import sha1

src= "C:\Music"
dst= "database\\"
thumbs= "image\\"

dumpdb= True

songs=[]
for (path,ndir,nfile) in walk(src):
    for name in nfile:
        songs.append(path+"\\"+name)

open(dst+"songs.txt","w").writelines(songs)

def Thumbnail(img):
    if img:
        h= sha1( img.data ).hexdigest();
        with open(thumbs+h,"wb") as out:
            out.write(img.data)
        return h
    return ""

songs=[]
def Song(f):
    i= EasyID3(f)
    s={
        "title": i["title"][0],
        "artist": i["artist"][0],
        "year": int(i["date"][0][:4]),
        "album": i["album"][0],
        "track": int(i["tracknumber"][0].split("/")[0]),
        "duration": int(i["length"][0])/1000,
        "musicbrainztrackid": i["musicbrainz_trackid"][0],
        "musicbrainzartistid": i["musicbrainz_artistid"][0],
        "musicbrainzalbumid": i["musicbrainz_albumid"][0],
        "musicbrainzalbumartistid": i["musicbrainz_albumartistid"][0],
        "file": f,
        "disc": int(i["discnumber"][0].split("/")[0]),
        "thumbnail": Thumbnail(i._EasyID3__id3["APIC:"]),
        "rating":0
        }
    print s["duration"]
    s["songid"]= len(songs)+1
    s["artistid"]= Artist(s)
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
         "artistid": s["artistid"],
         "rating":0
         }
    newid= len(albums)+1
    a["albumid"]=newid
    albums.append(a)
    albumid[ s["album"] ]= newid
    return newid

for (path,ndir,nfile) in walk(src):
    for name in nfile:
        Song(path+"\\"+name)
         
if dumpdb:
    dump( songs, open(dst+"songs.json","w"))
    dump( artists, open(dst+"artists.json","w"))
    dump( albums, open(dst+"albums.json","w"))
