from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os
from base64 import b64encode, b64decode
import json
from hex_to_bin import hex_to_bin

# added by Khanh - 13/10/2024

IV_LENGTH = 16
KEY_LENGTH = 16

PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"
CHOSEN_HASH = hashes.SHA256()

def encryptMessage(plaintext: str, participants, pub_keys: list):
    
    chat = {}
    chat['participants'] = []
    chat['message'] = plaintext
    
    for participant in participants:
        # fingerprint = hashlib.sha256(participant.encode('utf-8')).digest()
        # print(f'{fingerprint}\n\n')
        # fingerprint = hashlib.sha256(participant.encode('utf-8')).hexdigest()
        chat['participants'].append(b64encode(participant.encode()).decode('utf-8'))
        # print(f'Fingerprint: {chat['participants']}\n\n')
        # print(f'Unhash: {[b64decode(user).decode() for user in chat['participants']]}\n\n')

    
    chat = json.dumps(chat).encode('utf8')
    

    iv = os.urandom(IV_LENGTH)
    
    sym_key = os.urandom(KEY_LENGTH)
    
    aes_gcm = AESGCM(sym_key)
    
    cipher_chat = aes_gcm.encrypt(iv, chat, None)
    # return ciphertext bytes with 16 bytes tag appended
    
    symm_keys = []
    
    for pub_key in pub_keys:
        if (isinstance(pub_key, bytes)):
            if (pub_key.find(PEM_FOOTER_PUBK.encode()) == -1 or pub_key.find(PEM_HEADER_PUBK.encode()) == -1):
                pub_key = pub_key.replace(PEM_FOOTER_PUBK.encode(),"").replace(PEM_HEADER_PUBK.encode(),"").strip()
                pub_key = PEM_HEADER_PUBK.encode() + '\n' + pub_key + '\n' + PEM_FOOTER_PUBK.encode()
            rsa_public = serialization.load_pem_public_key(pub_key)
        elif (isinstance(pub_key, str)):
            if (pub_key.find(PEM_FOOTER_PUBK) == -1 or pub_key.find(PEM_HEADER_PUBK) == -1):
                pub_key = pub_key.replace(PEM_FOOTER_PUBK,"").replace(PEM_HEADER_PUBK,"").strip()
                pub_key = PEM_HEADER_PUBK + '\n' + pub_key + '\n' + PEM_FOOTER_PUBK
            rsa_public = serialization.load_pem_public_key(pub_key.encode())
        else:
            return False
        
        assert isinstance(rsa_public, rsa.RSAPublicKey) == True
        
        try:
            enc_key = rsa_public.encrypt(sym_key,
                                     padding.OAEP(
                                          mgf=padding.MGF1(CHOSEN_HASH),
                                          algorithm=CHOSEN_HASH,
                                          label=None)
                                    )
        except:
            raise ValueError("Message too long")
        encoded_enc_key = b64encode(enc_key).decode('utf8')
        symm_keys.append(encoded_enc_key)

    
    
    return cipher_chat, iv, symm_keys

def decryptMessage(ciphertext: bytes, iv: bytes, enc_sym_keys):
    with open("private_key_pem_pass.txt", "rb") as file:
        pwd = file.read()
    
    with open("./private_key.pem","rb") as private_file:
        try:
            private_key = serialization.load_pem_private_key(
                private_file.read(), 
                pwd)
        except ValueError as e:
            raise ValueError(f"Key format errors: {e}")
        except TypeError as e:
            raise TypeError(f"Password related erros: {e}")
    
    decoded_enc_keys = [b64decode(key) for key in enc_sym_keys]
    for enc_sym_key in decoded_enc_keys:
        try:
            decrypted_sym_key = private_key.decrypt(
                                    enc_sym_key,
                                    padding.OAEP(
                                        mgf=padding.MGF1(CHOSEN_HASH),
                                        algorithm=CHOSEN_HASH,
                                        label=None)
                                )
            break
        except:
            continue
    try:
        aes_gcm = AESGCM(decrypted_sym_key)
        chat = aes_gcm.decrypt(iv, ciphertext, None)
    except Exception as e:
        return False
    try:
        chat = json.loads(chat.decode('utf-8'))
        # chat['participants'] = [b64decode(user.encode('utf8')).decode() for user in chat['participants']]
        for i in range(len(chat['participants'])):
            decoded = b64decode(chat['participants'][i].encode('utf8'))
            try: 
                hex = decoded.decode('utf8')
                chat['participants'][i] = hex_to_bin(hex)
            except UnicodeDecodeError:
                chat['participants'][i] = hex_to_bin(decoded)
    except Exception as e:
        raise e
    
    return chat


#for testing this module seperately from the main program
if __name__ == "__main__":
    msg = "hello world"
    with open("./private_key.pem","r") as pub_file:
        pub_key = pub_file.read()
        # pub_key = pub_key.replace(pem_footer_pubk, "").replace("\n", "").strip()

    cipher_chat, iv, enc_keys = encryptMessage(msg,["kai1","kai2"],["-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmAg+kjPnhrvBeDH4+KKi\nRQByru6d1M+5dz7GCfcG+zJaziPP5/czhXvHo73dDB+d2XJmUko+k8C/Ws7cVVno\nPY6fBbpDfL1M0Q1apLG2cJpsCO7vHRConkxX92DxnYz6RCnxvfrDH2cH+3reh7ky\nTAKkiax7ouqB5peqMBxg6fBpOct+5jDoiY0271PwUbxxtzt9w9sYQ2VWX9WXkQ0C\nHhGmUJAK9kTLdvPmgJ6PBIg1jwXvGTMPAl7SRvNkCjHTKtLY4b3FFvKt0xpEsf4L\nwewtgFgoebKsNvsFRWdaT9neLZ//qYt0dJQUglExyTtEjsm9iuDt4pJXq+Ak+EYG\nAQIDAQAB\n-----END PUBLIC KEY-----","-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsLlTWSQDw2Y/O7aQoa2p\nhXwT+G5vOixr60W6tVkEdTofsz/ZRgxXdTe8YJEEcot/G6GpYLBB5s1dTYuGPlbM\nZx6vCoalopyYKxvuz7vPMEISL14VnUjZ5khqyMxop1aobbyrTXvE8TlERVFwwivm\nH4VPtbeTiXpruo8eOn+ghbpSxOKzqMabbUtqrJ/UvxIU1z4iYMjL3L8xVDN085mg\ntVT8K2dFAW7pND9AUBweFJTlUqgkD7jUzF4s6XC1ZDmmRSlX/4TtFDhG+LJZVkZi\nemM3uq8/8X/xGqw02mLQNP8Vo91ciw0TwwL1N2Vld/xuNshK/qk44lISVJQJ3b2s\nuQIDAQAB\n-----END PUBLIC KEY-----"])
    print(f"{cipher_chat}\n{iv}\n{enc_keys}")

    deciphered = decryptMessage(cipher_chat, iv, enc_keys) 
    print(f"\n{deciphered}")
    