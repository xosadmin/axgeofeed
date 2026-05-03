from models.sqlmodel import userAsset, geofeed

def checkCompetent(data, requiredValues):
    if not isinstance(requiredValues, list):
        return False
    if not isinstance(data, dict):
        return False
    return set(data.keys()) == set(requiredValues)

def convertGeofeed(data, userid):
    if not isinstance(data, dict):
        return False
    requiredValues = ["assetid", "included_in_geofeed", "prefix", "country_code", "region_code", "city", "postal_code"]
    if not checkCompetent(data, requiredValues):
        return False
    newObject = geofeed(
        userid=userid,
        assetid=data["assetid"],
        included_in_geofeed=data["included_in_geofeed"],
        prefix=data["prefix"],
        country_code=data["country_code"],
        region_code=data["region_code"],
        city=data["city"],
        postal_code=data["postal_code"]
    )
    return newObject

def convertASSet(data, userid):
    if not isinstance(data, dict):
        return False
    requiredValues = ["assetid"]
    if not checkCompetent(data, requiredValues):
        return False
    newObject = userAsset(
        userid=userid,
        assetid=data["assetid"],
        systemCreated=False
    )
    return newObject