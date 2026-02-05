import socket
import struct
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set send buffer
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2147483647)

addr = ("127.0.0.1", 9009)
seq = 0

sock.sendto(b'STOP', addr)
'''
start = time.time()
end_time = start + 10

while time.time() < end_time:
    packet = struct.pack('Q', seq) + b'\x00' * 8  # 8 bytes seq + 8 bytes padding = 16 bytes
    sock.sendto(packet, addr)
    seq += 1

# Send stop signal
sock.sendto(b"STOP", addr)

elapsed = time.time() - start
pps = seq / elapsed
mbps = (16 * pps * 8) / 1000000.0

print(f"Packets sent: {seq}")
print(f"Time elapsed: {elapsed:.6f}s")
print(f"PPS: {pps:.2f}")
print(f"Mbps: {mbps:.2f}")

sock.close()'''