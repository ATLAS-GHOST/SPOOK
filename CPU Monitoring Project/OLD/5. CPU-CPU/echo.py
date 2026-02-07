import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Huawei: Max buffer size: (2,147,483,647 bytes = 268435455 * 8  + 7)
# HP :    Max buffer size: 425 984
buffer_size =  2_147_483_647    #try to do byte allignment for optimisation

try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
    actual_buffer = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print(f"Socket send buffer set to: {actual_buffer:,} bytes")
except Exception as e:
    print(f"Warning: Could not set buffer size: {e}")


#same max as sender buffer size: 268435455 * 8  + 7
buffer_size = 268435455 * 8  + 7

#socket.SO_RCVBUF absorbs packets when loop cant keep up. When full, kernel drops packets. 


addr = ("192.168.1.44", 9001)
sock.bind(("0.0.0.0", 9000))

print("ECHO UDP PORT 9000: LISTENING")

try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
    actual_buffer = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print(f"Socket receive buffer set to: {actual_buffer:,} bytes")
except Exception as e:
    print(f"Warning: Could not set buffer size: {e}")
    print("UDP PORT 9000: CLOSED")    #remove this after done
    sock.close()

sock.bind(("0.0.0.0", 9000))
print("UDP PORT 9000: LISTENING")


try:
    while True:
        data, addr = sock.recvfrom(65536)  #caps per packet read size (bytes)     
        sock.sendto(data, addr)

except KeyboardInterrupt:
    print("UDP PORT 9000: CLOSED")
    sock.close()

