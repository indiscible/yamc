from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from os import walk
from json import dump
from hashlib import sha1

src= "C:\Music"
thumbs= "Thumbs\\"

dumpdb= True

songs=[]
for (path,ndir,nfile) in walk(src):
    for name in nfile:
        songs.append(path+"\\"+name)

open("songs.txt","w").writelines(songs)

def Thumbnail(img):
    if img:
        h= sha1( img.data ).hexdigest();
        with open(thumbs+h,"wb") as out:
            out.write(img.data)
        return h
    return ""

songid=0
def Song(f):
    i= EasyID3(f)
    global songid
    songid= songid+1    
    return {
        "title": i["title"][0],
        "artist": i["artist"][0],
        "year": int(i["date"][0][:4]),
        "album": i["album"][0],
        "track": int(i["tracknumber"][0].split("/")[0]),
        "duration": int(i["length"][0]),
        "musicbrainztrackid": i["musicbrainz_trackid"][0],
        "musicbrainzartistid": i["musicbrainz_artistid"][0],
        "musicbrainzalbumid": i["musicbrainz_albumid"][0],
        "musicbrainzalbumartistid": i["musicbrainz_albumartistid"][0],
        "file": f,
        "disc": int(i["discnumber"][0].split("/")[0]),
        "songid":songid,
        "thumbnail": Thumbnail(i._EasyID3__id3["APIC:"]),
        "rating":0
        }


db= []
for s in songs:
    db.append( Song(s) )        

if dumpdb:
    dump(db, open("songs.json","w"))
