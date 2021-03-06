from werkzeug.wrappers import Request, Response
from werkzeug.serving import make_server
from select import select
import subprocess
import json
import event
import yamc
import plugin
import playlist
import vlc
import audiolibrary
import database
from hashlib import sha1
import logging
import signal
import sys
import traceback
logging.basicConfig(filename="server.txt",level=logging.DEBUG)
def reply(j):
    try:
        e= yamc.execute(j)
    except: 
        print "error executing ", j
        print sys.exc_info()
        for line in traceback.format_tb( sys.exc_info()[2] ):
            print line
        return { "id": j["id"], "jsonrpc":"2.0", "error":
                 { "code": 0, "message": "eerror" } }
    return { "id": j["id"], "jsonrpc":"2.0", "result": e }

def post( d ):
    try:
        r=[]
        j= json.loads(d)
        if isinstance(j,list):
            for jj in j:
                r.append(reply(jj))
        else:
            r= reply(j)            
    except (AttributeError,TypeError,ValueError) as e:
        print "Error:",e, d
        return Response( "", mimetype='application/json')
    r= json.dumps(r)
    #print r
    return Response(  r, mimetype='application/json')

def get(d):
    if  d=="jsonrpc":
        return Response( "", mimetype='text/plain' )
    idx=d.find("/")
    if idx<0:
        return Response( "", mimetype='text/plain' )        
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
        print "Get:", request.data, request.full_path
        return get(request.full_path[1:-1])

def init():
    server= make_server('', 8001, app)
    server.protocol_version= "HTTP/1.1"
    return server,[ server.socket, event.make_udp(), event.make_tcp() ]
    
if not locals().has_key("server"):
    server,ss= init()
    print "server started"
    print server
    print ss

def close():
    global ss
    for s in ss:
        s.close()
    ss= None
    print "serve stopped"
    database.dumpdb()
    print "database stored"

def sigint(signal,frame):
    close()
    sys.exit(0)
signal.signal(signal.SIGINT,sigint)


def filehash(file):
    with open(file,"rb") as inp:
        return sha1(inp.read()).hexdigest()

def go():
    libs= { yamc:"", event:"", playlist:"",
            vlc:"", plugin:"", audiolibrary:"",
            database:"" }
    while(1):
        print "Waiting for request"
        rl = select( ss, [], [])
        for i in libs.items():
            h= filehash(i[0].__name__+".py")
            if h!=i[1]:
                print "new hash: ", i[0].__name__
                reload(i[0])
                libs[i[0]]= h
        for r in rl[0]:
            if r==ss[0]:
                print "http"
                server.handle_request()
            elif r==ss[1]:
                print "udp"
                yamc.handleudp(ss[1])
            elif r==ss[2]:
                print "tcp"
                event.handletcp(ss[2])
            else:
                print "bad select", r
                        
go()
