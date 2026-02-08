# SPOOK
SPOOK (Systems Performance &amp; Operational Observability Kit) visualises performance metrics on the trigger system.  

Make sure to download docker, node_exporter, promtheus_client

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
