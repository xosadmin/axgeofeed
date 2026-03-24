# axgeofeed
AXGeofeed - Automatic Geofeed Generator

## Installation
**A. Use Docker Engine**  
1. Clone this project
2. Build a docker container image: ``docker build -t axgeofeed .``
3. Load ``db.sql`` to your database, and finalise ``config.yaml`` config. For example, please refer to [example-config.yaml](https://github.com/xosadmin/axgeofeed/blob/main/example-config.yaml)
4. Use following command to run a container:
```
docker run -d --name axgeofeed \
-e TZ=<timezone> \
-p 5000:5000 \
-v /path/to/config.yaml:/app/config.yaml \
axgeofeed
```
  
Note: the default GUI/API port is 5000/tcp. It is recommend to use reverse proxy or WAF to enhance security.  
  
## Prefix List Auto Sync  
AXGeofeed supports automatically add prefix to geofeed list based on existing IRR records from RIR.  
In order to proceed with auto sync, you need to:
- Have a valid AS-SET associated to your ASN number, and added to AXGeofeed database
- Add ``IRR`` and ``Route6`` object for your prefix
- Setup Crontab ACL address in ``config.yaml``
- Setup Crontab task with ``<frequency> curl "http://127.0.0.1:5000/cron``, where port can be changed based on your configuration

## Geofeed outputs
A. CSV Format
- For all users: ``http://<address>/geofeed``
- For specific user: ``http://<address>/geofeed/<username>``
B. JSON Format
- For all users: ``http://<address>/geofeed/json``
- For specific user: ``http://<address>/geofeed/json/<username>``
  