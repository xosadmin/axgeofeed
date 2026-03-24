import uuid

def uuidGen():
    return str(uuid.uuid4())

def userIDGen():
    trim = uuidGen().split("-")[0]
    return trim