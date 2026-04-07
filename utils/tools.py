import uuid
from datetime import datetime

def uuidGen():
    return str(uuid.uuid4())

def userIDGen():
    trim = uuidGen().split("-")[0]
    return trim

def factor_disable(rawvalue):
    if rawvalue == "0":
        disabled = False
    else:
        disabled = True
    return disabled

def dateConvert(input):
    try:
        datetime_obj = datetime.strptime(input, "%Y-%m-%d")
        return datetime_obj
    except ValueError:
        return False