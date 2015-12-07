import BaseHTTPServer
import SocketServer

PORT = 83

jsonrpc= open("jsonrpc").read();
print len(jsonrpc)
def print_request(s):
    print s.command, s.path

class TheHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log(s):
        print s.command, s.path
    def do_HEAD(s):
        s.log()
        s.send_response(200)
        s.send_header("Content-Type","application/json")
        s.send_header("Content-Length", len(jsonrpc) )
        s.send_header("Connection", "Keep-Alive" )
        s.end_headers()
    def do_GET(s):
        s.log()
        s.send_response(200)
        s.send_header("Content-type","application/json")
        s.send_header("Content-length", len(jsonrpc) )
        s.send_header("Connection", "Keep-Alive" )
        s.end_headers()
        s.wfile.write(jsonrpc)
        print "done serving file"
    def do_POST(s):
        s.log()
        


#Handler = TheHandler
TheHandler.protocol_version='HTTP/1.1'

httpd = SocketServer.TCPServer(('192.168.0.13', PORT), TheHandler)

print "serving at port", PORT
httpd.serve_forever()
