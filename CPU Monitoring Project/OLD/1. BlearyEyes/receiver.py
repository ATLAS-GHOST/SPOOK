import socket, time
from prometheus_client import Counter, Gauge, start_http_server

class Metrics():
    def __init__(self):
        self.total_packets = 0
        self.packet_count = 0
        self.last_packet_time = None
        self.total_delta = 0
        self.jitter_count = 0
    
    def update_jitter(self, timestamp):
        if self.last_packet_time:
            delta = timestamp - self.last_packet_time
            self.total_delta += delta
            self.jitter_count += 1
        self.last_packet_time = timestamp
    
    def compute_jitter(self):
        if self.jitter_count > 0:
            return self.total_delta/self.jitter_count
        return 0
        
    def reset_periodic(self):
        self.packet_count = 0
        self.total_delta = 0
        self.jitter_count = 0
        
class Reporter():
    def report(self, metrics: Metrics): 
        raise NotImplementedError
    
class PrintReporter(Reporter):
    def report(self, metrics: Metrics):
        print(f"Total Packets: {metrics.total_packets}, PPS: {metrics.packet_count}, Jitter: {metrics.compute_jitter()*1000:.3f} ms")

class PrometheusReporter():
    def __init__(self, port=8000):
        start_http_server(port)
        self.total_packets = Counter(
            "udp_total_packets", 
            "Total number of packets received"
        )
        self.pps = Gauge(
            "udp_packets_per_second",
            "Number of packets arriving per second"
        )
        self.jitter = Gauge(
            "udp_jitter_ms",
            "Average time between two consecutive packets in 1 second"
        )
        print(f"Prometheus Metrics exposed on http://localhost:{port}/metrics")

    def report(self, metrics: Metrics):
        self.total_packets.inc(metrics.packet_count)
        self.pps.set(metrics.packet_count)
        self.jitter.set(metrics.compute_jitter() * 1000)
         
def setup_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 9000))
    print("UDP receiver listening on port 9000")
    return sock
         
         
def main_loop():
    sock = setup_socket()
    metrics = Metrics()

    print_reporter = PrintReporter()
    prometheus_reporter = PrometheusReporter(8000)

    start_time = time.time()
    
    try:
        while True:
            time_now = time.time()
            data, addr = sock.recvfrom(2048)
            metrics.total_packets += 1      #keeps track of total packets received
            metrics.packet_count += 1       #keeps track of packets in 1 sec
            metrics.update_jitter(time_now)

            #print(data.decode('utf-8'))
            
            
            if time_now - start_time >= 1:
                print_reporter.report(metrics)
                prometheus_reporter.report(metrics)
                metrics.reset_periodic()
                start_time = time_now
            
            #data.close() ???
                
    except KeyboardInterrupt:
        print("Server Stopped")

if __name__ == "__main__":
    main_loop()
