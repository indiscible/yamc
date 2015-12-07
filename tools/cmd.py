import socket

IP= '192.168.0.16'
PORT= 9090

s= socket.socket( socket.AF_INET, socket.SOCK_STREAM)
s.connect( ( IP, PORT) )

while(1):
    s.setblocking(1)
    s.send( '{"jsonrpc": "2.0", "method": "' + raw_input(">") + '", "id": 1}')
    s.setblocking(0)
    while True:
        try: 
            data= s.recv(4096)
            length= len(data)
            print "("+str(length)+") " + data
        except socket.error as msg:
            print  msg
            break
