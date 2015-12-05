import socket
import time
cmd='XBMC\x02\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08P\x80\x19+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01Mute()\x00'

client= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1)

while(1):
    client.sendto( cmd, ('127.0.0.1',9777) )
    time.sleep(1)
