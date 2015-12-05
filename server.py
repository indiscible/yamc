import gevent
import gevent.wsgi
import gevent.queue
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher

dispatcher = RPCDispatcher()
json = RPCDispatcher()
application= RPCDispatcher()
xbmc= RPCDispatcher()

dispatcher.add_subdispatch( json, "JSONRPC." )
dispatcher.add_subdispatch( application, "Application." )
dispatcher.add_subdispatch( xbmc, "XBMC." )

transport = WsgiServerTransport(queue_class=gevent.queue.Queue)

# start wsgi server as a background-greenlet
wsgi_server = gevent.wsgi.WSGIServer(('192.168.0.13', 8001), transport.handle)
gevent.spawn(wsgi_server.serve_forever)

rpc_server = RPCServerGreenlets(
    transport,
    JSONRPCProtocol(),
    dispatcher
)

@dispatcher.public
def reverse_string(s):
    return s[::-1]

@dispatcher.public
def jsonrpc():
    return "hello"

@json.public
def Ping():
    return "pong"

@application.public
def GetProperties(**kwargs):
    for p in kwargs["properties"]:
        print p
    return {'version':
            { 'major':15,
              'tag':'stable',
              'minor':2,
              'revision':'unknown'} } 
@xbmc.public
def GetInfoBooleans(**kwargs):
    for p in kwargs["booleans"]:
        print p
    return { "System.Platform.Linux.RaspberryPi": True,
             "System.Platform.Linux": True }

@xbmc.public
def GetInfoLabels(**kwargs):
    for p in kwargs["labels"]:
        print p
    return { 'System.KernelVersion': 'Busy',
             'System.BuildVersion':'15.2' }
# in the main greenlet, run our rpc_server
rpc_server.serve_forever()
