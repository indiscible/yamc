import struct
import json
import socket

header= struct.Struct("!4scchiihi10c")

cmd='XBMC\x02\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08P\x80\x19+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01Mute()\x00'

def unpackstring(b):
    return str( b[:b.find('\x00')])
def execute(p):
    h= header.unpack(p[:32])
    print h
    if h[3]==10:
        c= unpackstring( p[33:] )
        print "execute: ", c
        eval(c)
    else:
        print "unknown command:", h[3]

clients={}

def post(d):
    msg= json.dumps( { "jsonrpc":"2.0",
                         "method":"Application.OnVolumeChanged",
                         "params": { "data": d, "sender":"xbmc" } } )
    bads=[]
    for c in clients:
        try:
            c.send( msg )
        except socket.error:
            bads.append(c)
    for b in bads:
        print "remove client:", c
        clients.pop(b)
        
class Application:
    muted= False
    volume= 50

    @classmethod
    def OnVolumeChanged(c):
        post( { "muted": c.muted, "volume": c.volume } )

def Mute():
    Application.muted= not Application.muted
    Application.OnVolumeChanged();

tcp= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('',9090))
tcp.listen(5)
tcp.settimeout(0.1)
udp= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind( ('',9777))
udp.settimeout(0.1)
while(1):
    try:
        (client,addr)= tcp.accept()
        print "new client:", client, addr
        clients[client]= addr
    except socket.error:
        pass
    try:
        cmd,addr= udp.recvfrom(1024)
    except socket.error:
        pass
    execute(cmd)
    
        
            

    
