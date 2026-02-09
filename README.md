# SPOOK
**SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.**

This is the documentation for running the localhost Grafana setup

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Docker Compose
- Python virtual environment (venv)
- node_exporter
- prometheus_client

Run Python-related components inside a virtual environment (`venv`).


## Setup Instructions

### 1. Download the Project Files

1. Go to **DownGit**:  
   ```https://downgit.github.io/#/home```
2. Paste the following repository path:  
   ```https://github.com/ATLAS-GHOST/SPOOK/tree/main/CPU%20Monitoring%20Project/OLD/4.%20LocalHost```
3. Download and extract the files.


### 2. Navigate to the Project Directory
1. cd `to/parent/folder/of/docker/files`


### 3. Starting Docker
1. Run:
   ```sudo systemctl start docker```


### 4. Launch Grafana & Prometheus

1. Choose one of the following:  

   **Unoptimised Grafana Docker**  
   `docker compose up -d`
   
      This has no optimisation to Grafana CPU & RAM usage

   **Optimised Grafana Docker**  
   `docker compose -f docker-compose-optimised.yml up -d`
   
      This limits Grafana to a maximum of 1 CPU core and 1024 MB of RAM 

   If needed, clean up old containers:  
   ```docker rm prometheus grafana```

### 5. Launching node_exporter

1. cd `/path/to/node_exporter`
2. run:
   ```./node_exporter```

   This is required for Grafana's ethernet and NIC packet metrics

### 6. (Optional) Increase the network buffer limits

1. ```sudo sysctl -w net.core.wmem_max=2147483647 && sudo sysctl -w net.core.rmem_max=2147483647```

### 7. Starting the receiver

1. In a new terminal, run `receiver.py`  

   Note: If you want to increase the buffer size, run instruction #6 and restart `receiver.py`

### 8. Accessing Grafana
In order to access Grafana, the receiver must be running

1. Open your browser and go to:
   ```http://localhost:3000/login```
2. Login and add Prometheus as a data source:
   ```http://localhost:9090```
3. Copy and paste the JSON from the directory into Grafana settings
4. Run each panel query individually

### 9. Starting the sender

1. In a new terminal, run `sender.py`


You should now see the Grafana dashboard becoming populated with metrics. Breathe a sigh of relief!

