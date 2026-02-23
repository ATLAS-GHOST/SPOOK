import socket
import time
import struct


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buffer_size =  2_147_483_647 

target_ip = input("Enter target IP address in the format ex. 192.168.1.x : ").strip()

try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
    actual_buffer = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print(f"Socket send buffer set to: {actual_buffer:,} bytes")
except Exception as e:
    print(f"Warning: Could not set buffer size: {e}")

addr = (target_ip, 9000)

duration_seconds = 600
start_time_ns = time.time_ns()
end_time_ns = start_time_ns + (duration_seconds * 10**9)

seq_num = 1


#min packets size of 16 (just the header)
packet_size = 64                      #bytes   (max for me was: 8 * 8188 = 65504 bytes. UDP MAX = 65507 payload)
payload = b'x' * (packet_size - 16)      #ASCII x value   (bytes)

#print(time.time())



try:
    while time.time_ns() < end_time_ns:
        timestamp_ns = time.time_ns()
        #header is now 12 bytes
        header = struct.pack('!Q Q', seq_num, timestamp_ns)     #! means most-sig. val first. Q is 64bit int (8bytes). d is double 8 bytes
        packet = header + payload

        sock.sendto(packet, addr)
        seq_num += 1

            
except KeyboardInterrupt:
    print("Sender Stopped")

finally:
    time.sleep(1)
    sock.sendto(b'STOP', addr)
    sock.close()
    time_elapsed_ns = time.time_ns() - start_time_ns
    pps = seq_num / (time_elapsed_ns * 10**-9)
    mbps =  (packet_size * pps) / 1_000_000    #megabits per second 

    print(f"Packets send: {seq_num - 1}")
    print(f"Time elapsed: {time_elapsed_ns * 10**-9 - 1}s")
    print(f"PPS: {pps:.2f}")
    print(f"MBPS: {mbps:.2f}")
    print(f"Packet Size: {packet_size:.2f}")



