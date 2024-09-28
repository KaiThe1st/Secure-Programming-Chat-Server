# from Cryptodome.Cipher import AES, PKCS1_OAEP
# from Cryptodome.Random import get_random_bytes
# from Cryptodome.PublicKey import RSA
# from Cryptodome.Hash import SHA256
# from rsaKeyGenerator import generate_key_pair
# import hashlib
# import sys
# import binascii
# from base64 import b64encode, b64decode
# import json

# IV_LENGTH = 16
# KEY_LENGTH = 32

# PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
# PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"

# # def encryptMessage(plaintext, participants, online_users):
    
# #     chat = {}
# #     chat["message"] = plaintext
# #     chat["participants"] = participants

    
# #     # message = json.dumps(chat["message"]).encode()
    
# #     chat = json.dumps(chat).encode()
    

# #     iv = get_random_bytes(IV_LENGTH)
    
# #     sym_key = get_random_bytes(KEY_LENGTH)
    
# #     with open("./public_key.pem", 'rb') as public_file:
# #         public_key = RSA.import_key(public_file.read())

# #     cipher_rsa = PKCS1_OAEP.new(public_key, SHA256)
# #     ENC_SYM_KEY = cipher_rsa.encrypt(sym_key)
    
# #     cipher_aes = AES.new(sym_key, AES.MODE_GCM, iv)
# #     cipher_chat, authTag = cipher_aes.encrypt_and_digest(chat)
    
# #     destination_servers = []
# #     symm_keys = []
         
    
# #     for participant in participants:
# #         destination_servers = []
# #         symm_keys = []
    
    
# #     return(cipher_chat, authTag, iv, ENC_SYM_KEY)

# def encryptMessage(plaintext, participants, online_users, pub_key):
    
#     chat = {}
#     chat["message"] = plaintext
#     chat["participants"] = participants

    
#     message = json.dumps(chat["message"]).encode()
#     chat = json.dumps(chat).encode('utf-8')
    

#     iv = get_random_bytes(IV_LENGTH)
    
#     sym_key = get_random_bytes(KEY_LENGTH)
    
    
#     if (pub_key.find(PEM_FOOTER_PUBK) == -1 or pub_key.find(PEM_HEADER_PUBK) == -1):
#         pub_key = pub_key.replace(PEM_FOOTER_PUBK,"").replace(PEM_HEADER_PUBK,"").strip()
#         pub_key = PEM_HEADER_PUBK + '\n' + pub_key + '\n' + PEM_FOOTER_PUBK
         
#     rsa_public = RSA.import_key(pub_key)
#     cipher_rsa = PKCS1_OAEP.new(rsa_public, SHA256)
#     ENC_SYM_KEY = cipher_rsa.encrypt(sym_key)
    
#     cipher_aes = AES.new(sym_key, AES.MODE_GCM, iv)
#     cipher_chat, authTag = cipher_aes.encrypt_and_digest(message)
    
#     destination_servers = []
#     symm_keys = []
         
    
#     for participant in participants:
#         destination_servers = []
#         symm_keys = []
    
    
#     return(cipher_chat, iv, ENC_SYM_KEY)

# # def decrypt_message(ciphertext, authTag ,iv, enc_sym_key):
# #     with open("./private_key.pem","rb") as private_file:
# #         private_key = RSA.import_key(private_file.read(),passphrase="G40")
    
# #     cipher_rsa = PKCS1_OAEP.new(private_key, SHA256)
# #     sym_key = cipher_rsa.decrypt(enc_sym_key)
# #     try:
# #         cipher = AES.new(sym_key, AES.MODE_GCM, iv)
# #         plain_text = cipher.decrypt_and_verify(ciphertext, authTag)
# #     except:
# #         return ('Incorrect decrypt')
# #     return plain_text.decode('utf-8')

# def decryptMessage(ciphertext, iv, enc_sym_key):
#     with open("./private_key.pem","r") as private_file:
#         private_key = RSA.import_key(private_file.read(), passphrase="G40")
    
#     cipher_rsa = PKCS1_OAEP.new(private_key, SHA256)
#     sym_key = cipher_rsa.decrypt(enc_sym_key)
#     # plain_text = bytearray()
#     try:
#         cipher = AES.new(sym_key, AES.MODE_GCM, iv)
#         plain_text = cipher.decrypt(ciphertext)
#     except:
#         return ('Incorrect decrypt')
#     return plain_text.decode('utf-8')


# if __name__ == "__main__":
#     msg = "hello world"
#     with open("./public_key.pem","r") as pub_file:
#         pub_key = pub_file.read()
        
#         # pub_key = pub_key.replace(pem_footer_pubk, "").replace("\n", "").strip()

#     cipher_chat, nonce, enc_key = encryptMessage(msg,'kai','kai', pub_key)
#     print(cipher_chat)

#     deciphered = decryptMessage(cipher_chat, nonce, enc_key) 
#     print(deciphered)

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from rsaKeyGenerator import generate_key_pair
import hashlib
import binascii
from base64 import b64encode, b64decode
import json

IV_LENGTH = 16
KEY_LENGTH = 32

PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"

# def encryptMessage(plaintext, participants, online_users):
    
#     chat = {}
#     chat["message"] = plaintext
#     chat["participants"] = participants

    
#     # message = json.dumps(chat["message"]).encode()
    
#     chat = json.dumps(chat).encode()
    

#     iv = get_random_bytes(IV_LENGTH)
    
#     sym_key = get_random_bytes(KEY_LENGTH)
    
#     with open("./public_key.pem", 'rb') as public_file:
#         public_key = RSA.import_key(public_file.read())

#     cipher_rsa = PKCS1_OAEP.new(public_key, SHA256)
#     ENC_SYM_KEY = cipher_rsa.encrypt(sym_key)
    
#     cipher_aes = AES.new(sym_key, AES.MODE_GCM, iv)
#     cipher_chat, authTag = cipher_aes.encrypt_and_digest(chat)
    
#     destination_servers = []
#     symm_keys = []
         
    
#     for participant in participants:
#         destination_servers = []
#         symm_keys = []
    
    
#     return(cipher_chat, authTag, iv, ENC_SYM_KEY)

def encryptMessage(plaintext, participants, pub_keys):
    
    chat = {}
    chat["participants"] = []
    chat["message"] = plaintext
    
    for participant in participants:
        # fingerprint = hashlib.sha256(participant.encode('utf-8')).digest()
        # print(f'{fingerprint}\n\n')
        fingerprint = hashlib.sha256(participant.encode('utf-8')).hexdigest()
        chat["participants"].append(b64encode(fingerprint.encode()).decode('utf-8'))
        # print(f'Fingerprint: {chat["participants"]}\n\n')
        # print(f'Unhash: {[b64decode(user).decode() for user in chat["participants"]]}\n\n')

    
    # message = json.dumps(chat["message"]).encode()
    chat = json.dumps(chat).encode('utf-8')
    

    iv = get_random_bytes(IV_LENGTH)
    
    sym_key = get_random_bytes(KEY_LENGTH)
    
    cipher_aes = AES.new(sym_key, AES.MODE_GCM, iv)
    cipher_chat, authTag = cipher_aes.encrypt_and_digest(chat) 
    
    symm_keys = []
    
    for pub_key in pub_keys:
        if (pub_key.find(PEM_FOOTER_PUBK) == -1 or pub_key.find(PEM_HEADER_PUBK) == -1):
            pub_key = pub_key.replace(PEM_FOOTER_PUBK,"").replace(PEM_HEADER_PUBK,"").strip()
            pub_key = PEM_HEADER_PUBK + '\n' + pub_key + '\n' + PEM_FOOTER_PUBK
         
        rsa_public = RSA.import_key(pub_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_public, SHA256)
        enc_key = cipher_rsa.encrypt(sym_key)
        encoded_enc_key = b64encode(enc_key).decode('utf8')
        symm_keys.append(encoded_enc_key)
        # symm_keys.append(enc_key)

     
         
    # for participant in participants:
    #     destination_servers = []
    #     symm_keys = []
    
    
    return(cipher_chat, iv, symm_keys)

# def decrypt_message(ciphertext, authTag ,iv, enc_sym_key):
#     with open("./private_key.pem","rb") as private_file:
#         private_key = RSA.import_key(private_file.read(),passphrase="G40")
    
#     cipher_rsa = PKCS1_OAEP.new(private_key, SHA256)
#     sym_key = cipher_rsa.decrypt(enc_sym_key)
#     try:
#         cipher = AES.new(sym_key, AES.MODE_GCM, iv)
#         plain_text = cipher.decrypt_and_verify(ciphertext, authTag)
#     except:
#         return ('Incorrect decrypt')
#     return plain_text.decode('utf-8')

def decryptMessage(ciphertext, iv, enc_sym_keys):
    with open("./private_key.pem","r") as private_file:
        private_key = RSA.import_key(private_file.read(), passphrase="G40")
    
    decoded_enc_keys = [b64decode(key) for key in enc_sym_keys]
    cipher_rsa = PKCS1_OAEP.new(private_key, SHA256)
    for enc_sym_key in decoded_enc_keys:
        try:
            decrypted_sym_key = cipher_rsa.decrypt(enc_sym_key)
            break
        except:
            continue
    try:
        cipher = AES.new(decrypted_sym_key, AES.MODE_GCM, iv)
        chat = cipher.decrypt(ciphertext)
        chat = json.loads(chat.decode('utf-8'))
        chat["participants"] = [b64decode(user.encode('utf8')).decode() for user in chat["participants"]]
    except:
        return ('Incorrect decrypt')
    return chat