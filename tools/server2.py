from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import dispatcher

class thejsonrpc(object):
    def Ping():
        return "pong"

dispatcher.build_method_map( thejsonrpc, "JSONRPC." )

class application(object):
    version= { 'major':15, 'tag':'stable', 'minor':2,'revision':'unknown'}
    volume= 50
    muted= False
    def GetProperties(**kwargs):
        for p in kwargs["properties"]:
            print p
        return { 'version': version }

dispatcher.Dispatcher.build_method_map( application, "Application." )

class xbmc(object):
    def GetInfoBooleans(**kwargs):
        for p in kwargs["booleans"]:
            print p
        return { "System.Platform.Linux.RaspberryPi": True,
                 "System.Platform.Linux": True }
    def GetInfoLabels(**kwargs):
        for p in kwargs["labels"]:
            print p
        return { 'System.KernelVersion': 'Busy',
                 'System.BuildVersion':'15.2' }

dispatcher.Dispatcher.build_method_map( xbmc, "Xbmc." )


@Request.application
def server(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher.Dispatcher)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    run_simple('192.168.0.13', 8001, application)
