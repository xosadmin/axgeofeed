import requests

def accessAPI(ipaddr):
    if "/" in ipaddr:
        ipaddr = ipaddr.split("/")[0]
    url = f"http://ip-api.com/json/{ipaddr}"
    try:
        req = requests.get(url, timeout=20)
        if req.status_code == 200:
            return req.json()
        else:
            return {}
    except Exception as e:
        print(f"Error when accessing ip-api: {e}")
        return {}

