# axgeofeed
AXGeofeed - Automatic Geofeed Generator

## Installation
**A. Use Docker Engine**  
1. Clone this project
2. Build a docker container image: ``docker build -t axgeofeed .``
3. Use following command to run a container:
```
docker run -d --name axgeofeed \
-e TZ=<timezone> \
-p 5000:5000 \
-v /path/to/config.yaml:/app/config.yaml \
axgeofeed
```
  
Note: the default GUI/API port is 5000/tcp. It is recommend to use reverse proxy or WAF to enhance security.  