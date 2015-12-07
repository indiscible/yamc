from werkzeug.wrappers import Request, Response
from werkzeug.serving import make_server
from select import select
import subprocess
import json
import event
import yamc
from hashlib import sha1

def reply(j):
    e= yamc.execute(j)
    return { "id": j["id"], "jsonrpc":"2.0", "result": e }

def error(code,message):
    return { "id": j["id"], "jsonrpc":"2.0", "error":
             { "code": code, "message": message } }

#Log= open("log.txt","w")
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
 #   print r
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
#    print request
#   print request.data
#   Log.write(request.data+"\n")
    global yop
    dir(request)
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

def filehash(file):
    with open(file,"rb") as inp:
        return sha1(inp.read()).hexdigest()

oldhash= filehash("yamc.py")
while(1):
    rl = select( ss, [], [])
    newhash= filehash("yamc.py")
    if newhash!=oldhash:
        print "new hash: ", newhash, oldhash
        reload(yamc)
        oldhash=newhash
    for r in rl[0]:
        if r==server.socket:
            #print "http"
            server.handle_request()
        elif r==event.udp:
            print "udp"
            xbmc.handleudp()
        elif r==event.tcp:
            print "tcp"
            event.handletcp()
        else:
            print "bad select", r
 #   event.run()
