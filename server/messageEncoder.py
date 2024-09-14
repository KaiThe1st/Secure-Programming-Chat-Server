from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib
import sys
import binascii
import base64

IV_LENGTH = 16
KEY_LENGTH = 32

def encrypt_message(plaintext):
    
    sym_key = get_random_bytes(KEY_LENGTH)
    iv = get_random_bytes(KEY_LENGTH)
    
    
    cipher = AES.new(sym_key, AES.MODE_GCM, iv)
    ciphertext, authTag = cipher.encrypt_and_digest(plaintext)
    return(ciphertext, authTag, iv, sym_key)

def decrypt_message(ciphertext, authTag, sym_key):
    # (ciphertext,  authTag, nonce) = ciphertext
    cipher = AES.new(sym_key, AES.MODE_GCM , iv)
    plain_text = cipher.decrypt(ciphertext)
    try:
        cipher.verify(authTag)
        return plain_text
    except:
        return ('wrong message')