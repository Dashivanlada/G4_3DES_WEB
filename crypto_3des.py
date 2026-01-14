from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64

IV = b'12345678'  # demo IV (8 bytes)

def derive_key(password: str) -> bytes:
    h = SHA256.new(password.encode('utf-8')).digest()
    return DES3.adjust_key_parity(h[:24])

def encrypt(plaintext: str, password: str) -> str:
    key = derive_key(password)
    cipher = DES3.new(key, DES3.MODE_CBC, IV)
    padded = pad(plaintext.encode('utf-8'), DES3.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt(ciphertext: str, password: str) -> str:
    key = derive_key(password)
    cipher = DES3.new(key, DES3.MODE_CBC, IV)
    decoded = base64.b64decode(ciphertext)
    decrypted = cipher.decrypt(decoded)
    return unpad(decrypted, DES3.block_size).decode('utf-8')
