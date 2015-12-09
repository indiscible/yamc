from werkzeug.wrappers import Request, Response
from werkzeug.serving import make_server
from select import select
import subprocess
import json
import event
import yamc
import vlc
from hashlib import sha1
import logging
import signal
import sys

def reply(j):
    e= yamc.execute(j)
    return { "id": j["id"], "jsonrpc":"2.0", "result": e }

def error(code,message):
    return { "id": j["id"], "jsonrpc":"2.0", "error":
             { "code": code, "message": message } }

def post( d ):
    try:
        r=[]
        j= json.loads(d)
        if isinstance(j,list):
            for jj in j:
                r.append(reply(jj))
        else:
            r= reply(j)            
    except ValueError as e:
        print e
        return Response( "", mimetype='application/json')
    r= json.dumps(r)
    return Response(  r, mimetype='application/json')

yopg=None

def get(d):
    if  d=="jsonrpc":
        return Response( "", mimetype='text/plain' )
    idx=d.find("/")
    if idx<0:
        return Response( "", mimetype='text/plain' )        
    global yopg
    yopg= d
    try:
        with open( d, "rb" ) as inp:
            return Response( inp.read(), mimetype='image/jpeg' )
    except IOError as e:
        print e
        return Response( "", mimetype='text/plain' )                
    raise Exception
    
@Request.application
def app(request):
    if request.method=="POST":
        return post(request.data)
    elif request.method=="GET":
        yop=request
        print "Get:", request.data, request.full_path
        return get(request.full_path[1:-1])
   
server= make_server('192.168.0.13', 80, app)
print "server started"
ss= [ server.socket, event.udp, event.tcp ]
def close():
    for s in ss:
        s.close()

def sigint(signal,frame):
    close()
    sys.exit(0)
signal.signal(signal.SIGINT,sigint)

def filehash(file):
    with open(file,"rb") as inp:
        return sha1(inp.read()).hexdigest()

libs= { yamc:"", vlc:"" }
print libs
while(1):
    rl = select( ss, [], [])
    for i in libs.items():
        h= filehash(i[0].__name__+".py")
        if h!=i[1]:
            print "new hash: ", i[0].__name__
            reload(i[0])
            libs[i[0]]= h
    for r in rl[0]:
        if r==server.socket:
            server.handle_request()
        elif r==event.udp:
            print "udp"
            yamc.handleudp()
        elif r==event.tcp:
            print "tcp"
            event.handletcp()
        else:
            print "bad select", r
 #   event.run()

