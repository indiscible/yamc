from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from tinyrpc import RPCClient
import json

client = RPCClient(
    JSONRPCProtocol(),
    HttpPostClientTransport('http://192.168.0.16/jsonrpc')
)

#reply=client.call("JSONRPC.Introspect","","")

#with open("introspect.json","w") as out:
#    json.dump(reply, out, indent=2)
