from utils.bcryptworks import encrypt_password
import base64

plaintext = input("Enter your plaintext: ")
encrypted = encrypt_password(plaintext)
hashed = base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')
print(hashed)