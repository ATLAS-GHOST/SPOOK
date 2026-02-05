import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set receive buffer
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2147483647) 

addr = ("0.0.0.0", 9009)
sock.bind(addr)

print("UDP PORT 9009: LISTENING")

data, _ = sock.recvfrom(1)

print(data)

    
