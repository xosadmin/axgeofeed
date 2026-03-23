from utils.bcryptworks import encrypt_password
import base64

plaintext = input("Enter your plaintext: ")
encrypted = encrypt_password(plaintext).decode('utf-8')
hashed = base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')
print(hashed)