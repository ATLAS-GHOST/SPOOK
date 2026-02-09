# SPOOK
SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.  

Make sure to download docker, node_exporter, promtheus_client - run in a venv

1. Head to DownGit: https://downgit.github.io/#/home
2. Enter: https://github.com/ATLAS-GHOST/SPOOK/tree/main/CPU%20Monitoring%20Project/OLD/4.%20LocalHost
3. Download & extract files
4. cd to/path
5. systemctl start docker
6. docker compose up -d (unoptimised grafana docker) or docker compose -f docker-compose-optimised.yml up -d (optimised docker)
7. docker rm prometheus grafana (if needed)
8. sudo sysctl -w net.core.wmem_max=2147483647 && sudo sysctl -w net.core.rmem_max=2147483647
9. cd to node_exporter in downloads in new terminal
10.  then do ./node_exporter
11.  new terminal
12.  Run the receiver
13.  HEad to grafana - http://localhost:3000/login
14.  Add Prometheus data source - http://localhost:9090 
15.  COpy grafanaJSON
16.  Start the sender in seperate terminal
17.  RUn queries indiviudally
18.  Breathe a sigh of relief

# SPOOK  
**Systems Performance & Operational Observability Kit**

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Docker Compose
- Python virtual environment (venv)
- node_exporter
- prometheus_client

Run Python-related components inside a virtual environment (`venv`).

---

## Setup Instructions

### 1. Download the Project Files

1. Go to **DownGit**:  
   ```https://downgit.github.io/#/home```
2. Paste the following repository path:  
   ```https://github.com/ATLAS-GHOST/SPOOK/tree/main/CPU%20Monitoring%20Project/OLD/4.%20LocalHost```
3. Download and extract the files.

---

### 2. Navigate to the Project Directory
1. cd `to/parent/folder/of/docker/files`


### 3. Starting Docker
1. Run:
   ```sudo systemctl start docker```


### 4. Launch Grafana & Prometheus

1. Choose one of the following:  

      **Unoptimised Grafana Docker**  
      ```docker compose up -d```

      **Optimised Grafana Docker**  
      ```docker compose -f docker-compose-optimised.yml up -d```

   If needed, clean up old containers:  
   ```docker rm prometheus grafana```

### 5. Launching node_exporter

1. cd `/path/to/node_exporter`
2. run:
   ```./node_exporter```


5. Increase Network Buffer Limits
sudo sysctl -w net.core.wmem_max=2147483647
sudo sysctl -w net.core.rmem_max=2147483647
6. Start Node Exporter
Open a new terminal, then:
cd /path/to/node_exporter
./node_exporter
7. Start the Receiver
Open another new terminal and run the receiver:
# command to run receiver
8. Access Grafana
Open your browser and go to:
http://localhost:3000/login
9. Configure Prometheus Data Source
In Grafana, add a new Prometheus data source
Set the URL to:
http://localhost:9090
Save & test the connection
10. Import Dashboard
Copy the provided grafanaJSON
Import it into Grafana
11. Start the Sender
In a separate terminal, start the sender:
# command to start sender
12. Run Queries
Execute queries individually in Grafana
Confirm metrics are updating correctly
