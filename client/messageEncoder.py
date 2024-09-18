from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib
import sys
import binascii
import base64 
import json

IV_LENGTH = 16
KEY_LENGTH = 32
SYM_KEY= get_random_bytes(KEY_LENGTH)

def encryptMessage(plaintext, participants, online_users):
    
    chat = {}
    chat["message"] = plaintext
    chat["participants"] = participants
    
    chat = json.dumps(chat).encode()
    

    iv = get_random_bytes(KEY_LENGTH)
    
    
    cipher = AES.new(SYM_KEY, AES.MODE_GCM, iv)
    cipher_chat, authTag = cipher.encrypt_and_digest(chat)
    
    destination_servers = []
    symm_keys = []
    
    for participant in participants:
        destination_servers = []
        symm_keys = []
    
    # cipher_chat = "hey"
    # authTag = ""
    
    return(cipher_chat, authTag, iv, SYM_KEY)


#my part

# def decrypt_message(ciphertext, authTag, sym_key):
#     # (ciphertext,  authTag, nonce) = ciphertext
#     cipher = AES.new(sym_key, AES.MODE_GCM , iv)
#     plain_text = cipher.decrypt(ciphertext)
#     try:
#         cipher.verify(authTag)
#         return plain_text
#     except:
#         return ('wrong message')