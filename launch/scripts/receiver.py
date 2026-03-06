import socket
import struct
import time
import psutil
import subprocess
import os
import glob
import docker
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
    sock.close()

sock.bind(("0.0.0.0", 9000))
print("UDP PORT 9000: LISTENING")


def find_nic_pcie_path():
    """Auto-detect NIC's PCIe device path"""
    for device_path in glob.glob('/sys/bus/pci/devices/*'):
        net_path = os.path.join(device_path, 'net')
        if os.path.exists(net_path):
            interfaces = os.listdir(net_path)
            for iface in interfaces:
                if iface != 'lo':
                    return device_path, iface
    return None, None

pcie_path, nic_name = find_nic_pcie_path()
print(f"Found NIC: {nic_name} at {pcie_path}")


def read_pcie_stats(pcie_path):
    stats = {}
    
    try:
        # Buffer overflow + packets dropped
        with open(os.path.join(pcie_path, 'aer_dev_nonfatal')) as f:
            for line in f:
                name, value = line.strip().split()
                if name == 'RxOF':
                    stats[name] = int(value)

    except Exception as e:
        print(f"Error reading PCIe stats: {e}")
    
    return stats

packets_received_p = Counter('packets_received_total', 'Total packets received')
bytes_received_p = Counter('bytes_received_total', 'Total bytes receved')
packets_lost_p = Counter('packets_lost_total', 'Total packets lost')
process_cpu_p = Gauge('process_cpu_usage', 'CPU usage of the reveiver')
total_cpu_p = Gauge('total_cpu_usage', 'Total CPU usage')
latency_p = Histogram('latency_ms', 'Packet latency in milliseconds',
                      buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 25, 50, 100])
grafana_cpu_usage_p = Gauge('grafana_cpu_usage', 'CPU usage of grafana')
grafana_mem_p = Gauge('grafana_memory_bytes', 'Grafana memory usage')
receiver_mem_p = Gauge('receiver_memory_bytes', 'Receiver memory usage')



# Docker client (connects to local Docker daemon)
docker_client = docker.from_env()

# Get container object
container = docker_client.containers.get("monitoring")



pcie_rx_overflow_p = Gauge('pcie_rx_overflow', 'PCIe buffer overflow')



count = 0
packets_received_last_sample = 0

expected_seq = 1
packets_lost = 0
packets_out_of_order = 0    #no packets out of order

cpu_samples = []
latencies = []
sampling_freq = []

seq_samples = []


start_http_server(8000)   #for prometheus

process = psutil.Process()


try:
    while True:
        data, addr = sock.recvfrom(65536)  #caps per packet read size (bytes)        

        if data == b'STOP':
            packets_lost_percent = (packets_lost / seq) * 100
            print(f"Packets Sent: {count+packets_lost}")
            print(f"Packets Received: {count}")   #bcs starts from -1
            print(f"Packets Lost: {packets_lost}")
            print(f"Packets Loss Percentage: {packets_lost_percent:.4f}")
            break

        seq = struct.unpack('!Q', data[:8])[0]
        #print(f'expected: {expected_seq}, seq: {seq}')
        sender_timestamp_ns = struct.unpack('!Q', data[8:16])[0]

        if expected_seq == seq:
            expected_seq += 1

        elif expected_seq < seq:
            packets_lost += (seq - expected_seq)
            packets_lost_p.inc(seq - expected_seq)
            expected_seq = seq + 1 

        elif expected_seq > seq:
            packets_out_of_order += 1 

        
        count += 1
        packets_received_p.inc()
        bytes_received_p.inc(len(data))
        latency_p.observe((time.time_ns() - sender_timestamp_ns)/1_000_000)

        if count % 1000 == 0:
            
            # Get process CPU usage (percentage of one CPU core)
            process_cpu_percent = process.cpu_percent(interval=0)
            
            # Get total system CPU usage (percentage across all cores)
            total_cpu_percent = psutil.cpu_percent(interval=0)
            
            # Update Prometheus metrics
            process_cpu_p.set(process_cpu_percent)
            total_cpu_p.set(total_cpu_percent)
            

            stats = container.stats(stream=False)

            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]

            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                        stats["precpu_stats"]["system_cpu_usage"]

            # Safe CPU core count handling
            percpu = stats["cpu_stats"]["cpu_usage"].get("percpu_usage")

            if percpu:
                cpu_count = len(percpu)
            else:
                cpu_count = os.cpu_count() or 1

            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100.0
            else:
                cpu_percent = 0.0

            # --- MEMORY ---
            memory_usage = stats["memory_stats"]["usage"]

            # Update Prometheus metrics
            grafana_cpu_usage_p.set(cpu_percent)
            grafana_mem_p.set(memory_usage)

            

            receiver_mem_p.set(process.memory_info().rss)


            if pcie_path:
                stats = read_pcie_stats(pcie_path)
                pcie_rx_overflow_p.set(stats.get('RxOF', 0))

       
except KeyboardInterrupt:
    print("UDP PORT 9000: CLOSED")
    sock.close()



    #potential:
    #pcie_rx_err_p = Gauge('pcie_rx_err', 'PCIe receive errors')
    # pcie_rx_overflow_p = Gauge('pcie_rx_overflow', 'PCIe buffer overflow')
    # pcie_tlp_lost_p = Gauge('pcie_tlp_lost', 'PCIe packets lost (TLP)')
    # pcie_nonfatal_p = Gauge('pcie_nonfatal_errors', 'PCIe nonfatal errors')
    # pcie_fatal_p = Gauge('pcie_fatal_errors', 'PCIe fatal errors')
