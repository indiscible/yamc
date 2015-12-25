import yamc
import external

print "soundcloud item"
print yamc.Player.Open( { "file":'plugin://plugin.audio.soundcloud/play//?url=https%3A%2F%2Fsoundcloud.com/wavveswavves/wavves-my-head-hurts' } )

#print "yamcs.Plyer.open.soundcloutd:", yamc.Player.Open( { "file":'plugin://plugin.audio.soundcloud/play/?url=https%3A%2F%2Fsoundcloud.com%2Fjorge-aboumrad-vega%2Fsets%2Fdreamon' } )

print "yam.Player.open:", yamc.Player.Open( { "songid":1 } )

print "yamc.Playlist.open:", yamc.Player.Open( { "file":'plugin://plugin.video.youtube/?action=play_video&videoid=B6jfrrwR10k' } )

print "open playlist:", yamc.Playlist.Open( playlistid=0, position=5 )


#yamc.Playlist.Add(item={ "file":'plugin://plugin.video.youtube/?action=play_video&videoid=B6jfrrwR10k' },playlistid=0)
#yamc.Player.Seek(playerid=0, value= {u'hours': 0, u'seconds': 22, u'minutes': 14})
#yamc.Player.GetProperties(playerid=0,properties=["duration"])
#yamc.Playlist.Add(item={ "file":'plugin://plugin.video.youtube/?action=play_video&videoid=B6jfrrwR10k' },playlistid=0)


