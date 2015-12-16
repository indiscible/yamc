import struct
import json
import socket
import sys
header= struct.Struct("!4scchiihi10c")

cmd='XBMC\x02\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08P\x80\x19+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01Mute()\x00'

def unpackstring(b):
    return str( b[:b.find('\x00')])

def button(p):
    flags= { 0x01: "USE_NAME",
             0x02: "DOWN",
             0x04: "UP",
             0x08: "USE_AMOUNT",
             0x10: "QUEUE",
             0X20: "NO_REPEAT",
             0X40: "VKEY",
             0X100: "AXISSINGLE"
    }
#    print p[:6]
#   print p[6:]
    code,flag,amount= struct.unpack("!hhh",p[:6])
    device,name,other= p[6:].split('\x00')
    print "button:", p
    print code,flag,amount,device,name
    f= { v for k,v in flags.items() if flag&k }
    if "DOWN" in f:
        return name+"()"

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
        b=button( p[32:] )
        try:
            eval(b,g,l)
        except:
            print "button error", sys.exc_info()[0],":", b
            
    elif h[3]==5:
        print "Ping"
    else:
        print "unknown command:", p

if not locals().has_key("clients"):
    global clients
    clients={}

def post(m,d):
    msg= json.dumps( { "jsonrpc":"2.0",
                         "method": m,
                         "params": { "data": d, "sender":"xbmc" } } )
    print msg
    bads=[]
    for c in clients:
        try:
            c.send( msg )
        except socket.error as e:
            print "send error:", clients[c], e
            if not e.errno == socket.errno.EPIPE:
                bads.append(c)
    for b in bads:
        print "remove client:", b
        clients.pop(b)

def make_tcp():
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',9090))
    s.listen(5)
    return s


def handletcp(tcp):
    (client,addr)= tcp.accept()
    print "new client:", client, addr
    clients[client]= addr

def make_udp():    
    s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind( ('',9777))
    print s
    return s

def handleudp(udp,g=globals(),l=locals()):
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
        
            

    
