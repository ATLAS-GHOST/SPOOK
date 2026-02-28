# SPOOK
**SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.**

This is the documentation for running the localhost and ethernet Grafana setup

## Prerequisites

Before you begin, make sure you have the following:

- A device running Linux with sudo permissions
- Docker
- Python virtual environment (venv)
- node_exporter
- prometheus_client
- Ports 8000 & 9100 free for receiver.py and node_exporter respectively for Prometheus scraping
     (If you want to change the ports, please do so manually in `prometheus.yml` for port 8000 and 9100 & `receiver.py` for port 8000 

Please run Python-related components inside a virtual environment (`venv`).

1. To run ethernet testing, you must have 2 machines available on the same network. The host machine runs the Docker container, and the receiver.py file. The second machine runs sender.py. You will need to add the IP of the host machine when prompted on the sender.py file. Data is sent via the network stack using UDP.
2. To run loopback testing, keep both files on the same machine, as well as the Docker container. Data does not travel through the wire in this testing.


## Setup Instructions

### 1. Clone the Project Files

In order to get the repository that containes all the file we need, run:

1. `git clone https://github.com/ATLAS-GHOST/SPOOK.git`

This will get the Docker folder, which containss the Dockerfile to launch Grafana & Prometheus via the entrypoint shell script. It will also get the launch files, which contain the receiver.py and sender.py, ready for packet testing. 

### 2. Launching Grafana

Navigate to the Docker directory using:

1. `cd docker`

And start Docker using: 

2. `sudo systemctl start docker`

Once Docker is running, we can build our image. The image is called monitoring-stack, and uses the current directory as the build context. Do this using:

3. `docker build -t monitoring-stack .`

This image is based on Alpine Linux, and is `HOW MANY MB IS IT? HOW MUCH CPU AND RAM DOES IT USE?`. Then,Prometheus and Grafana binaries are downloaded from GitHub, unzipped, and residuals are deleted. Configuration files are then added:

   a. `prometheus.yml` provides the 3 endpoints for Prometheus to scrape. These are 'prometheus', 'udp_receiver' and 'node'. 'udp_receiver' is the receiver.py file running on the host system, and 'node' is the node_exporter endpoint, which gives valuable NIC metrics used in Grafana. Both use the Linux default Docker bridge gateway '172.17.0.1' and are connected to ports 8000 and 9100 respectively. `FUNCTIONAILITY TO CHOOSE WHICH PORT?`

   b. `datasources.yml` ensures that the Promethes datasource is already configured in the Grafana dashboard, making it the default datasource. It also ensures the UID of prometheus is consitent.

   c. `dashboard.yml` creates the directory to store the dashboards in Docker 
   
   d. `dashboard.json` stores the JSON for the premade dashboard, which will automatically load up on start

Then, the entrypoint script is copied over, which will allow Docker to run Prometheus and Grafana in the background, and listen to ports 9090 & 3000 respectively. The script also ends in "$@" which replaces the shell with any commands given with `docker run`
   
After we have built our Docker image, we can run the image. Grafana and Prometheus are in one image to reduce the complexity of the system, and to reduce the network travel of packets between two hypothetical, seperate images. Run it in the terminal with:

4. ```
   docker run -d \
   -p 9090:9090 -p 3000:3000 \
   --name monitoring \
   --cpus="1.0" \
   --memory="1024m" \
   monitoring-stack \
   sleep infinity
   ```

This command runs the `monitoring-stack` image in detached mode (using -d, which frees up the terminal for other commands), names is `monitoring` and assigns a local Prometheus & Grafana ports of 9090 and 3000 to Docker's port of 9090 and 3000 respectively. You can change the local port you want to use by changing the initial port supplied in the command, as such: `-p <YOUR-PORT>:9090 -p <YOUR-PORT>:3000`. This command also limits Grafana to a maximum of 1 CPU core and 1024 MB of RAM. Lastly, the command `sleep infinity` ensures the program does not exit after the final command has been completed

If needed, clean up old containers which may have similar names:  
   ```docker rm prometheus grafana monitoring```

### 8. Starting node_exporter

Now, it is important you launch node_exporter, which allows for ethernet and NIC packet metrics visualisation in Grafana. In order to start node_exporter after downloading it:

5. `cd /path/to/node_exporter` and then `./node_exporter` in a new terminal.

This will now send metrics to `http://localhost:9100/` and can be accessed there

### 8. Accessing Grafana via web UI 

In order to access Grafana via the web UI:

6. Open your browser and go to: `http://localhost:3000/login`
   
There, you should login using admin/admin and optionally change your login details. Please wait up to 5 minutes for the URL to work. Once logged in, the SPOOK dashboard is premade, just navigate to it. When looking at the panels, you must check what ethernet label your device uses and fix the PromQL accordingly for some of the panels. The default is set to 'eno1', but it varies with different devices. 

It is optimal to increase the buffer limits on the sender and host machines to reduce the number of packets dropped due to overflow. You can do this by running in a new terminal:

7. `sudo sysctl -w net.core.wmem_max=2147483647 && sudo sysctl -w net.core.rmem_max=2147483647`

Ideally, this should be run on the host and the sender machines. You can change the maximum number to your pleasing, but the default set here is 2GB.

### 8. Starting the receiver

To start the receiver: 
8. In a new terminal, cd `SPOOK/launch/scripts/` and run `receiver.py`  

If you want to increase the buffer size, run instruction #7 and restart `receiver.py`

### 9. Starting the sender

9. In a new terminal, cd `SPOOK/launch/scripts/`and run the script. An example input for the sender is `python sender.py --target-ip 127.0.0.1 --buffer 4000 --duration 10 --packet-size 16`, where: 
   a. `--target-ip` is the IP address of the machine which hosts the Prometheus and Grafana Docker. If not typed out, it will default to local host "0.0.0.0". Format it without quotation marks.  
     Example: `--target-ip 192.168.2.xx` or ` ` to default to localhost
    
   b. `--buffer` is the size of the OS send buffer in bytes. By increasing it, more packets can be sent per second with reduced latency. If set too low, packets will back-up in the buffer and will be sent once the buffer drains. Any incoming packets on a full buffer will be dropped due to the UDP. It defaults to 2_147_483_647 bytes, but it depends on the OS restrictions in place, as some OS will cap max buffer sizes.  
     Example: `--buffer 640000000` or ` ` for default
   
   c. `--duration` is for how long the sender should send the UDP packets. It defaults to 60 seconds.  
     Example: `--duration 600` for 10 minutes or ` ` for 60 seconds.
   
   d. `--packet_size` is how big the UDP packets are. This has a minimum value of 16 bytes, to a maximum  

You should now see the Grafana dashboard becoming populated with metrics on the URL `http://localhost:3000/`. If any metrics are broken, please ensure the the PromQL is targeting the correct metric, especially ethernet. 

### 9. Stopping the Docker container

To stop the container and its images, run:

10. docker stop monitoring && docker rm monitoring
