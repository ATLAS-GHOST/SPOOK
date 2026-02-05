#FINAL AND CORRECT AS OF 27-12-2025 19:22
import socket
import time
import random
import psutil
from collections import deque
import zlib
import struct
import threading


#connection setup for UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 9000)

#setting up the socket buffer of 2MB 
desired_buffer_size = 2 * 1024 * 1024  # 2MB
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, desired_buffer_size)

#get actual buffer size 
actual_buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
print(f"UDP send buffer size: {actual_buffer_size} bytes ({actual_buffer_size/1024:.1f} KB)")

last_send_latency_us = 0.0     #initialised to 0 for first packet sending

#initialising metrics
client_num = random.randint(1, 100)
bunch_crossing_id = 0
next_bunch_crossing_time = time.time_ns() #initial time to start loop

psutil.cpu_percent(interval=None) #None (default) to mean that it measures against prev call. It is first call here

process_cpu_percent = 0.0  #Global for CPU metrics
cpu_usage_smoothed = 0.0
cpu_mhz = 0.0  
mem_percent = 0.0
process_mem_mb = 0.0
p = psutil.Process()  # for memory usage

count = 0

def update_cpu_metrics():
    global process_cpu_percent
    global cpu_usage_smoothed
    global cpu_mhz
    global mem_percent
    global process_mem_mb
    p_local = psutil.Process()  # Separate Process object for thread
    p_local.cpu_percent()   #prime
    while True:
        process_cpu_percent = p_local.cpu_percent(interval=1)
        cpu_usage_smoothed = psutil.cpu_percent(interval=1)
        freq = psutil.cpu_freq()    #may not work on containers!!!
        cpu_mhz = freq.current if freq else 0  
        mem_percent = psutil.virtual_memory().percent  
        process_mem_mb = p_local.memory_info().rss / (1024 * 1024)  #rss = resident set size in byte
        time.sleep(1)

# Start CPU monitoring thread
threading.Thread(target=update_cpu_metrics, daemon=True).start()

start_time = time.monotonic()    #why not monotonic?
packets_sent = 0

duration_seconds = 60   #how long to send for
bunch_crossing_interval_ns = 20_000    #what KHz to send at 1_000_000 (~1000pps) do not change as its hardcoded in receiver
#when 10,000ns = 100,000pkt/s but we hit limit and it jumps to 22583.7
#20,000 = 50,000pkt/s but still kumps to max
#40,000 = 25,000pkt/s but still at max 
#50_000 = 20,000pkt/s - reliably hitting on linux hp laptop
detector_hit_prob = 0.05    #prob of getting a hit

#track 
packet_size = struct.calcsize(">I Q Q H B f f f f f f") + 4  # packet + checksum

packet_format = ">I Q Q H B f f f f f f"
packet_struct = struct.Struct(packet_format)   #precompiles the struct

try:
    while (time.monotonic() - start_time) < duration_seconds:
        timestamp_ns = time.time_ns()
        if timestamp_ns >= next_bunch_crossing_time:
            bunch_crossing_id += 1
            next_bunch_crossing_time += bunch_crossing_interval_ns
            
            
            #generating hit detection simulation
            #change to [0] * 16 not append if it makes it quicker
            #clean this code up and break it down
            has_hit = random.random() < detector_hit_prob
            detector_hits = [0] * 16
            if has_hit:
                for i in range(16):
                    prob = 0.8 if 9 <= i <= 12 else 0.2  #higher chance of hitting 9 to 12
                    detector_hits[i] = 1 if random.random() < prob else 0
                if not any(detector_hits):
                    detector_hits[random.randint(0, 15)] = 1   #random channel given 1 hit

            #0 1, 1 0,  2 0,  3 1 
            
            #convert the list to binary for UDP sending
            detector_bits = sum(hit << i for i, hit in enumerate(detector_hits))  #the RHS gets converted to binary and then added 

            num_hits = sum(detector_hits)

            trigger_quality = 0

            if num_hits > 0:
                random_value = random.uniform(-25, 45)  #offset calc for detector
                trigger_quality = min(100, max(0, num_hits * 8 + random_value)) #artificial trigger quality metric

 
            packet_bytes = packet_struct.pack(
                    client_num,
                    bunch_crossing_id,
                    time.time_ns(),
                    detector_bits,
                    int(trigger_quality),
                    cpu_usage_smoothed,
                    process_cpu_percent,
                    cpu_mhz,
                    mem_percent,
                    process_mem_mb,
                    last_send_latency_us
            )

            #although the python udp sends a checksum anyway and automaitcally checks, i did one for learning purposes
            checksum = zlib.crc32(packet_bytes)
            checksum_bytes = struct.pack(">I", checksum)  #why is the > needed?

            start_send_time = time.perf_counter_ns()
            sock.sendto(packet_bytes + checksum_bytes, addr)
            last_send_latency_us = (time.perf_counter_ns() - start_send_time) / 1000
            
            packets_sent += 1
        
        else:
            slack_ns = 5_000   #ensures program wakes slightly before next packet, however may not be effective due to being too precise and not effective
            #better than using the interval to sleep as this will wake up slighlty before. it also reduces drift because the program gap is now relative to prev time
            #reduces drift at the cost of packets. 
            sleep_time = max(0, (next_bunch_crossing_time - timestamp_ns - slack_ns)/ 1e9)
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print("Sender stopped")

sock.close()
elapsed = time.monotonic() - start_time
print(f"\nSender finished: {packets_sent} packets in {elapsed:.2f}s ({packets_sent/elapsed:.1f} pkt/s)")



#LOTS OF PACKET LOSS DUE TO MOVING THE CALCULATION INTO A DIFFERENT THREAD
#move as much as possible to different thread
#limit of 1_000_000_000 due to windows os :( it just resorts to 43k pkts/s
#not using monotonic as it is same initialisation in receiver and sender so latency measurements are wrong
