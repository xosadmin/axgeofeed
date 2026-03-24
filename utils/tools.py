import uuid

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