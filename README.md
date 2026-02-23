# SPOOK
**SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.**

This is the documentation for running the localhost and ethernet Grafana setup

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Python virtual environment (venv)
- node_exporter
- prometheus_client

and run Python-related components inside a virtual environment (`venv`).


## Setup Instructions

### 1. Download the Project Files

1. run `git clone https://github.com/ATLAS-GHOST/SPOOK.git`

### 2. Navigate to the Project Directory
1. run `cd docker`

### 3. Starting Docker
1. run `sudo systemctl start docker`

### 4. Launch Grafana & Prometheus

1. Run Grafana & Prometheus Docker with `docker run -d -p 9090:9090 -p 3000:3000 --name monitoring monitoring-stack sleep infinity`
   
      This limits Grafana to a maximum of 1 CPU core and 1024 MB of RAM 

   If needed, clean up old containers:  
   ```docker rm prometheus grafana```


### 5. Accessing Grafana
In order to access Grafana:

1. Open your browser and go to:
   ```http://localhost:3000/login```
2. The dashboard is premade, just navigate to it
3. You must check what ethernet label your device uses and fix the PromQL accordingly

### 6. Launching node_exporter

1. cd `/path/to/node_exporter`
2. run `./node_exporter`

   This is required for Grafana's ethernet and NIC packet metrics

### 7. (Optional) Increase the network buffer limits

1. ```sudo sysctl -w net.core.wmem_max=2147483647 && sudo sysctl -w net.core.rmem_max=2147483647```

### 8. Starting the receiver

1. In a new terminal, cd `SPOOK/launch/scripts/`
2. run `receiver.py`  

   Note: If you want to increase the buffer size, run instruction #6 and restart `receiver.py`

### 9. Starting the sender

1. In a new terminal, cd `SPOOK/launch/scripts/`
2. run `sender.py`


You should now see the Grafana dashboard becoming populated with metrics.

