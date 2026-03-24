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
  
**Note: the default GUI/API port is 5000/tcp. It is recommended to use reverse proxy or WAF to enhance security.**  
  
## Prefix List Auto Sync  
AXGeofeed will use the configured AS-SET to resolve prefixes from ``IRR route / route6`` objects during scheduled sync.
To enable auto-sync, please ensure that:
- A valid ``AS-SET`` is associated with your ASN and has been added to the AXGeofeed database
- Valid ``route and/or route6 IRR`` objects exist for your prefixes
- The cron ACL address is configured in ``config.yaml``
- A cron task is set up to call ``http://127.0.0.1:5000/cron`` at your desired interval, for example:
```
    <frequency> curl -s "http://127.0.0.1:5000/cron"
```

## Geofeed outputs
#### A. CSV Format
- For all users: ``http://<address>/geofeed``
- For specific user: ``http://<address>/geofeed/<username>``  
#### B. JSON Format
- For all users: ``http://<address>/geofeed/json``
- For specific user: ``http://<address>/geofeed/json/<username>``
  