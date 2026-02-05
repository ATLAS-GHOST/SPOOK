#FINAL AND CORRECT AS OF 27-12-2025 19:22
import socket
import time
import struct
import zlib
from prometheus_client import start_http_server, Counter, Gauge, Histogram

#setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9000))
print("UDP Receiver listening on port 9000\n")

#counters
total_packets_received = 0
packets_this_second = 0
checksum_errors = 0
last_arrival_time = None
last_bunch_crossing_id = None
expected_interval_ns = 20_000  #should be same in sender - hardcoded here
start_time = time.monotonic_ns()

start_http_server(port=8000)

#prometheus initialisation
packets_received = Counter('udp_packets_received_total', 'Total packets received')
packets_per_second = Gauge('udp_packets_per_second', 'Packets received per second')
checksum_errors_total = Counter('udp_checksum_errors_total', 'Total checksum errors')
detector_hits = Histogram('detector_hits', 'Number of detector hits', buckets=[i+0.5 for i in range(17)]) #0.5, 1.5, 2.5 etc ... 16.5
detector_channel_hits = Counter("detector_channel_hits_total", "Total hits per detector channel", ["channel"]) #channel value

trigger_quality_metric = Gauge('trigger_quality', 'Trigger quality value')
cpu_usage = Gauge('sender_cpu_usage_smoothed', 'Sender CPU usage smoothed')
process_cpu = Gauge('sender_process_cpu_percent', 'Sender process CPU percent')
cpu_freq = Gauge('sender_cpu_mhz', 'Sender CPU frequency MHz')
memory_percent = Gauge('sender_mem_percent', 'Sender memory percent')
process_memory = Gauge('sender_process_mem_mb', 'Sender process memory MB')

client_gauge = Gauge('client_number', 'Client number')
packet_latency = Histogram('packet_latency_us', 'Packet Latency in microseconds', buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 25000, 50000, 75000, 100000, 150000, 200000, 300000, 500000])

#packet_jitter should really be scaled with the interval time from the sender
packet_jitter = Histogram('packet_jitter_us', 'Packet Jitter in microseconds', buckets = [1, 5, 10, 50, 100, 200, 500, 1000, 5000, 10000])
inter_arrival_time = Histogram('packet_inter_arrival_time_us', 'TIme between packet arrivals in microseconds', buckets = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000, 4000, 5000, 7500, 10000])
packets_out_of_order = Counter('packets_out_of_order', 'Packets not received in order')
packets_lost = Counter('packets_lost_total', 'Packets lost')

#buffer mterics
send_latency_us = Gauge('sender_udp_time_us', 'Sender time in microseconds')



packet_format = ">I Q Q H B f f f f f f"  
buffer_size = 2048   #can we shrink this?

try:
    while True:
        data, addr = sock.recvfrom(buffer_size)
        receive_time = time.time_ns()  #trial

        #split packet and checksum
        packet_bytes = data[:-4]   #checksum is 4 bytes at end
        checksum_bytes = data[-4:]

        #verify checksum - although redundant on UDP Python
        received_checksum = struct.unpack(">I", checksum_bytes)[0] #how does this work
        computed_checksum = zlib.crc32(packet_bytes)

        if received_checksum != computed_checksum:   #add more functionality here?
            checksum_errors += 1
            checksum_errors_total.inc()
            print(f"Checksum error! Expected {computed_checksum}, got {received_checksum}")
            continue

        #unpack packet
        unpacked = struct.unpack(packet_format, packet_bytes)
        client_num = unpacked[0]
        bunch_crossing_id = unpacked[1]
        timestamp_ns = unpacked[2]
        detector_bits = unpacked[3]
        trigger_quality = unpacked[4]
        cpu_usage_smoothed = unpacked[5]
        process_cpu_percent = unpacked[6]
        cpu_mhz = unpacked[7]
        mem_percent = unpacked[8]
        process_mem_mb = unpacked[9]
        last_send_latency_us = unpacked[10]  

        #calculate packet arrival and jitter times

        if last_arrival_time is not None:
            arrival_time_ns = receive_time - last_arrival_time
            arrival_time_us = arrival_time_ns / 1000

            inter_arrival_time.observe(arrival_time_us)

            #check for out of order
            if bunch_crossing_id <= last_bunch_crossing_id:
                packets_out_of_order.inc()
            else:
                #checking for lost packets
                expected_id = last_bunch_crossing_id + 1
                if bunch_crossing_id > expected_id:
                    lost = bunch_crossing_id - expected_id
                    packets_lost.inc(lost)
                
                #jitter
                sequence_gap = bunch_crossing_id - last_bunch_crossing_id
                expected_interval_gap_ns = expected_interval_ns * sequence_gap
                jitter_ns = abs(arrival_time_ns - expected_interval_gap_ns)
                jitter_us = jitter_ns / 1000
                packet_jitter.observe(jitter_us)

        last_arrival_time = receive_time
        last_bunch_crossing_id = bunch_crossing_id


        #detect which channel was hit
        for channel in range(16):
            if detector_bits & (1 << channel):
                detector_channel_hits.labels(channel=f"{channel:02d}").inc() #adds padding for sorting


        #detect num of hits in detector
        num_hits = bin(detector_bits).count('1')  #binary rep of bits

        latency_ns = receive_time - timestamp_ns
        latency_us = latency_ns / 1_000
        packet_latency.observe(latency_us)  #use percentiles in grafana querying
        

        # Update Prometheus metrics
        packets_received.inc()
        detector_hits.observe(num_hits)    #ex: detector_hits_buckets{le = "0"} +=1 if num_hits <=0  etc
        trigger_quality_metric.set(trigger_quality)
        cpu_usage.set(cpu_usage_smoothed)
        process_cpu.set(process_cpu_percent)
        cpu_freq.set(cpu_mhz)
        memory_percent.set(mem_percent)
        process_memory.set(process_mem_mb)
        client_gauge.set(client_num)
        send_latency_us.set(last_send_latency_us)

        #update counters
        total_packets_received += 1
        packets_this_second += 1  #am i even using this in grafana?

        #this can be removed!
        if receive_time - start_time >= 1_000_000_000:
            packets_per_second.set(packets_this_second)
            #print(f"Packets #{total_packets_received-packets_this_second+1}-{total_packets_received},"
            #      f"PPS: {packets_this_second}")
            #print(f"Latency: {latency_us}, receive time: {receive_time}, send time: {timestamp_ns}")
        
            #reset
            packets_this_second = 0
            start_time = receive_time


except KeyboardInterrupt:
    print("\nReceiver Stopped")

print("Receiver Stopped. Closing port!")
#reset all the vars here
sock.close()


'''
Common causes:

OS scheduler - Python isn't real-time, OS can pause your process
CPU core switching - Process moved to different core
Python garbage collection - Occasional GC pauses
Other system activity - Background processes, kernel tasks
'''