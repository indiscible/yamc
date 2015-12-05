import struct
import json
import socket

header= struct.Struct("!4scchiihi10c")

cmd='XBMC\x02\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08P\x80\x19+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01Mute()\x00'

def unpackstring(b):
    return str( b[:b.find('\x00')])

def button(p):
    code,flag,amount= struct.unpack("!iii",p[:12])
    device,name= p[12:].split('\x00')
    print "button:", p
    print code,flag,amount,device,name
def hello(p):
    print "Hello: ", p
def execute(p,g,l):
    h= header.unpack(p[:32])
    print h
    if h[3]==1:
        hello(p[32:])
    elif h[3]==10:
        c= unpackstring( p[33:] )
        print "execute: ", c
        eval(c,g,l)
    elif h[3]==3:
        button( p[32:] )
    elif h[3]==5:
        print "Ping"
    else:
        print "unknown command:", p


clients={}

def post(d):
    msg= json.dumps( { "jsonrpc":"2.0",
                         "method":"Application.OnVolumeChanged",
                         "params": { "data": d, "sender":"xbmc" } } )
    print msg
    bads=[]
    for c in clients:
        try:
            c.send( msg )
        except socket.error:
            bads.append(c)
    for b in bads:
        print "remove client:", c
        clients.pop(b)

tcp= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('192.168.0.13',9090))
tcp.listen(5)
tcp.settimeout(1)

def handletcp():
    (client,addr)= tcp.accept()
    print "new client:", client, addr
    clients[client]= addr
    
udp= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind( ('',9777))
udp.settimeout(1)

def handleudp(g=globals(),l=locals()):
    cmd,addr= udp.recvfrom(1024)
    execute(cmd,g,l)

def run():
    try:
        (client,addr)= tcp.accept()
        print "new client:", client, addr
        clients[client]= addr
    except socket.error:
        pass
    try:
        cmd,addr= udp.recvfrom(1024)
    except socket.error as e:
        pass
    else:       
        execute(cmd)
        
            

    
