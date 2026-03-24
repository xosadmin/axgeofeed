import subprocess
from models.sqlmodel import geofeed
from utils.assetworks import sanitize_asset
from utils.ipapi import accessAPI

def runBGPQ4(asset):
    asset = sanitize_asset(asset)

    commands = [
        ["bgpq4", "-4", "-F", "%n/%l\n", asset],
        ["bgpq4", "-6", "-F", "%n/%l\n", asset]
    ]
    prefixes = []

    try:
        for cmd in commands:
            run = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=80
            )
            output = run.stdout.decode("utf-8")

            for line in output.splitlines():
                prefix = line.strip()
                if not prefix:
                    continue
                prefixes.append(prefix)

        return prefixes

    except Exception as e:
        print(f"Error running bgpq4 for {asset}: {e}")
        return []


def query_prefix_to_list(query):
    if not query:
        return []
    return [item.prefix for item in query]


def query_asset_to_list(query):
    if not query:
        return []

    assets = []
    for item in query:
        if str(item.asset_name).endswith("_MANUAL"):
            continue
        assets.append({
            "userid": item.userid,
            "assetid": item.id,
            "assetname": item.asset_name,
        })
    return assets


def wrapper(queryAssetResult, queryPrefixResult):
    if not queryAssetResult:
        return []

    outputs = []
    assets = query_asset_to_list(queryAssetResult)
    existing_prefix_set = set(query_prefix_to_list(queryPrefixResult))

    for asset in assets:
        new_prefixes = runBGPQ4(asset["assetname"])

        for prefix in new_prefixes:
            if prefix in existing_prefix_set:
                continue

            ipinfo = accessAPI(prefix)

            if len(ipinfo) == 0:
                statement = geofeed(
                    userid=asset["userid"],
                    assetid=asset["assetid"],
                    prefix=prefix,
                    country_code="NA"
                )
            else:
                statement = geofeed(
                    userid=asset["userid"],
                    assetid=asset["assetid"],
                    prefix=prefix,
                    country_code=ipinfo["countryCode"],
                    region_code=f"{ipinfo["countryCode"]}-{ipinfo['region']}",
                    city=ipinfo["city"],
                    postal_code=ipinfo["zip"],
                )
            outputs.append(statement)
            existing_prefix_set.add(prefix)

    return outputs