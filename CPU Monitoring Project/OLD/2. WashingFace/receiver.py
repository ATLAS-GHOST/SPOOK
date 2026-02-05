import socket
import struct
import time
import statistics
import psutil
import matplotlib.pyplot as plt
import numpy as np
from prometheus_client import start_http_server, Counter, Gauge, Histogram

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#same max as sender buffer size: 268435455 * 8  + 7
buffer_size = 268435455 * 8  + 7

#socket.SO_RCVBUF absorbs packets when loop cant keep up. When full, kernel drops packets. 


try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
    actual_buffer = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print(f"Socket receive buffer set to: {actual_buffer:,} bytes")
except Exception as e:
    print(f"Warning: Could not set buffer size: {e}")
    print("UDP PORT 9000: CLOSED")    #remove this after done
    sock.close()

sock.bind(("127.0.0.1", 9000))
print("UDP PORT 9000: LISTENING")


#packets_received = Counter('packets_received', 'Total packets received')
#bytes_received = Counter('bytes_received', 'Total bytes received')

count = 0

expected_seq = 0
packets_lost = 0
packets_out_of_order = 0    #no packets out of order

cpu_samples = []
latencies = []
sampling_freq = []

seq_samples = []

psutil.cpu_percent(interval=None)

try:
    while True:
        data, addr = sock.recvfrom(65536)  #caps per packet read size (bytes)        

        if data == b'STOP':
            packets_lost_percent = (packets_lost / seq) * 100
            jitter = statistics.stdev(latencies)

            print(f"Packets Sent: {count+packets_lost}")
            print(f"Packets Received: {count}")   #bcs starts from -1
            print(f"Packets Lost: {packets_lost}")  
            print(f"Packets Loss Percentage: {packets_lost_percent:.4f}")

            latencies.sort()
            n = len(latencies)
            
            print(f"\nTotal samples recorded: {len(latencies)}")

            print(f"Min: {latencies[0]/1000:,.3f} μs")
            print(f"P50 (median): {latencies[n//2]/1000:,.3f} μs")
            print(f"P90: {latencies[int(n*0.90)]/1000:,.3f} μs")
            print(f"P99: {latencies[int(n*0.99)]/1000:,.3f} μs")
            print(f"P99.9: {latencies[int(n*0.999)]/1000:,.3f} μs")
            print(f"Max: {latencies[-1]/1000:,.3f} μs")
            print(f"Average: {sum(latencies)/n/1000:,.3f} μs")

            print(f"Jitter: {jitter:,.0f} ns ({jitter/1000:.3f} μs)")
            
            print(f"\nAvg CPU: {sum(cpu_samples)/len(cpu_samples):.1f}%")
            print(f"Peak CPU: {max(cpu_samples):.1f}%")


            #print(seq_samples)
            #print(cpu_samples)
            print(latencies)

            # After your existing stats printout (after "break")
            # Create histogram with normal distribution overlay
            plt.figure(figsize=(12, 6))

            # Convert to microseconds for better readability
            latencies_us = [lat/1000 for lat in latencies]

            # Create histogram
            n, bins, patches = plt.hist(latencies_us, bins=20, density=True, alpha=0.7, 
                                        color='blue', edgecolor='black', label='Actual Data')

            # Fit and plot normal distribution
            mu = np.mean(latencies_us)
            sigma = np.std(latencies_us)
            x = np.linspace(min(latencies_us), max(latencies_us), 100)
            normal_dist = (1/(sigma * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu)/sigma)**2)
            plt.plot(x, normal_dist, 'r-', linewidth=2, label=f'Normal Dist (μ={mu:.2f}, σ={sigma:.2f})')

            plt.xlabel('Latency (μs)')
            plt.ylabel('Probability Density')
            plt.title(f'Latency Distribution (n={len(latencies):,} samples)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            break
        
        expected_seq += 1  #count
        seq = struct.unpack('!Q', data[:8])[0]
        sender_timestamp_ns = struct.unpack('!Q', data[8:16])[0]
        if expected_seq != seq:
            packets_lost += (seq - expected_seq)
            expected_seq = seq 
        
        count += 1
        
        

        if (expected_seq) % 1000 == 0:
            cpu_samples.append(psutil.cpu_percent(interval=None))
            travel_time_ns = time.time_ns() - sender_timestamp_ns
            latencies.append(travel_time_ns)
            sampling_freq.append(seq)
            seq_samples.append((seq, expected_seq))#what waas expected for that sequence
            

        
except KeyboardInterrupt:
    print("UDP PORT 9000: CLOSED")
    sock.close()




'''

            
'''