# SPOOK
**SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.**

This is the documentation for running the UDP packet testing software. It can be run on ethernet or localhost. Before we clone the code, we need some prerequisites.

## 0. Prerequisites

Before you begin, ensure the following requirements are met:

A Linux device with sudo permissions

Docker installed

Python with a virtual environment (venv)

Ports 9090, 3000, 4318, and 9464 available for Prometheus, Grafana, the OTEL receiver, and the OTEL exporter

All Python scripts should be run inside a virtual environment (`venv`).

SPOOK can operate in two deployment modes:

1. Distributed (multiple devices)
The machine running the Docker container acts as the host, running Prometheus, Grafana, and the OpenTelemetry Collector. Metric generator scripts can run on multiple other devices on the same network. Each script must be configured with the IP address of the host machine so it can send metrics to the OTEL receiver.

2. Local / Loopback testing
All components (Docker container and generator scripts) run on the same machine, using localhost for communication.


## Setup Instructions

### 1. Clone the Project Files

In order to get the repository that containes all the file we need, run:

1. ```git clone https://github.com/ATLAS-GHOST/SPOOK.git```

This will get the Docker folder, which contains the Dockerfile to launch Grafana, OTEL & Prometheus via the entrypoint shell script. It will also get the script files, which contain the metric generators. 

Create a virtual environment, where we can install all our dependancies:

2. `cd SPOOK`

Then create a virtual environment:

3. `python3 -m venv venv`

Then activate the environment by:

4. `source venv/bin/activate`

Install dependencies:

5. `pip install --upgrade pip`
6. `pip install prometheus_client psutil docker opentelemetry-sdk opentelemetry-api opentelemetry-exporter-otlp opentelemetry-semantic-conventions`

### 2. Launching The Grafana & Prometheus Docker

Navigate to the Docker directory using:

1. `cd docker`

And start Docker using: 

2. `sudo systemctl start docker`

Once Docker is running, we can build our image. The image is called monitoring-stack, and uses the current directory as the build context. Do this using:

3. `docker build -t monitoring-stack .`

Prometheus, Grafana, and OTEL binaries are downloaded and configured:

   a. `prometheus.yml` sets up targets including the OTEL metrics endpoint (:9464).

   b. `datasources.yml` sets Prometheus as Grafana’s default datasource.

   c. `dashboard.yml` creates the directory to store the dashboards in Docker 
   
   d. `dashboard.json` provides a pre-made dashboard automatically loaded on startup.

   e. `otel-collector-config` allows for metrics to be collected in one location and scraped via Prometheus

The entrypoint script launches Prometheus, OTEL, and Grafana. The script also ends in "$@" which replaces the shell with any commands given with `docker run`
   
Run the container:

4.  
   ```
   docker run -d \
  -p 9090:9090 -p 3000:3000 -p 4318:4318 -p 9464:9464 \
  --name monitoring \
  --cpus="1.0" \
  --memory="1024m" \
  monitoring-stack
   ```

9090 → Prometheus UI
3000 → Grafana UI
4318 → OTLP receiver (metrics ingestion from scripts)
9464 → Prometheus exporter endpoint for scraping. This command also limits Grafana to a maximum of 1 CPU core and 1024 MB of RAM.

5. If needed, clean up old containers which may have similar names:  
   ```docker rm monitoring```

### 3. Running the Metrics Generators (Scripts)

Sender / generator scripts:

Copy scripts to remote machines or keep local for loopback testing.

Use argparse to provide the collector IP. Example:

`python fake_gpu_metrics.py --collector-ip 192.168.1.42`

`--collector-ip` defaults to localhost if omitted

Scripts send OTLP metrics to `http://<collector-ip>:4318/v1/metrics`

Example script snippet:
`exporter = OTLPMetricExporter(endpoint=f"http://{collector_ip}:4318/v1/metrics")`

### 4. Accessing Grafana and Prometheus UI 

Grafana: `http://localhost:3000/login`

Prometheus: `http://localhost:9090/targets`

Default Grafana login: `admin/admin`

### 5. Snapshotting Metrics

You can save a Prometheus snapshot:

1. `cd /SPOOK/snapshot`

2. run `./snapshot_prometheus.sh`

This saves a snaphot of all the metrics till current in the folder `./prometheus_snapshot`

3. Copy the ID of the snapshot including parent folder. Example:

`./prometheus_snapshot/20260311T144551Z-0acced28a0e1b105`


### 6. Restoring Prometheus snapshots

1. in the `SPOOK/snapshot` directory, run `./restore_snapshot.sh `<location-of-id>`. Example:

`./restore_snapshot.sh ./prometheus_snapshot/20260311T144551Z-0acced28a0e1b105`

This stops Prometheus container, overwrites TSDB, and starts container again.

Grafana will display metrics from the snapshot.

### 7. Verifying application health & Useful links

To verify:

  1. Docker - Run `Docker ps` and `monitoring` should be running, or the name you gave when running it. You should also see that the ports are mapped properly
     
  2. Grafana Web - Open `http://localhost:3000`. If Grafana UI appears, then it is running well
     
  3. Prometheus - Open `http://localhost:9090/targets`. There, you should see 3 targets; udp_receiver, prometheus & node. All 3 should be showing as UP
     
  4. OTEL endpoints - Open `http://localhost:9464/metrics`. You should see the metrics exposed by the OTEL there

### 8. Stopping the Docker container

To stop the container and its images, run:

1. `docker stop monitoring && docker rm monitoring`


