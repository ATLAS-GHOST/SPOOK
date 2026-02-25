#!python sender.py --target-ip 127.0.0.1 --buffer 0 --duration 10 --packet-size 16
import socket
import time
import struct
import argparse
import sys

def main(target_ip, buffer_size, duration_seconds, packet_size):
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  try:
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
      actual_buffer = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
      print(f"Socket send buffer set to: {actual_buffer:,} bytes")
  except Exception as e:
      print(f"Warning: Could not set buffer size: {e}")

  addr = (target_ip, 9000)

  start_time_ns = time.time_ns()
  end_time_ns = start_time_ns + (duration_seconds * 10**9)

  seq_num = 1


  #min packets size of 16 (just the header)
                #bytes   (max for me was: 8 * 8188 = 65504 bytes. UDP MAX = 65507 payload)
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
      for i in range(0,100):
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

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="UDP Sender")
  parser.add_argument("--target-ip", required=True, help="Local network target IP address ex. 192.168.1.x")
  parser.add_argument("--buffer", type=int, default=2_147_483_647, help="Sender OS buffer size in bytes")
  parser.add_argument("--duration", type=int, default=10, help="How long to send the packets for in seconds")
  parser.add_argument("--packet-size", type=int, default=1400, help="Packet size in bytes")

  args = parser.parse_args()

  main(args.target_ip, args.buffer, args.duration, args.packet_size)
