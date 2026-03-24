import bcrypt
import base64

def encrypt_password(plaintext):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plaintext.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def encrypt_hash_base64(hashedtext):
    hashed = base64.b64encode(hashedtext.encode('utf-8')).decode('utf-8')
    return hashed

def verifyPassword(plaintext, hashed):
    try:
        hashed = base64.b64decode(hashed)
    except Exception as e:
        raise ValueError("Failed to decode base64 encoded password hash.") from e

    if bcrypt.checkpw(plaintext.encode('utf-8'), hashed):
        return True
    else:
        return False