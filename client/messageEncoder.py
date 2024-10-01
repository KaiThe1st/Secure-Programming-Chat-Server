from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from rsaKeyGenerator import generate_key_pair
import hashlib
from base64 import b64encode, b64decode
import json

IV_LENGTH = 16
KEY_LENGTH = 16

PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"

def encryptMessage(plaintext, participants, pub_keys):
    
    chat = {}
    chat["participants"] = []
    chat["message"] = plaintext
    
    for participant in participants:
        # fingerprint = hashlib.sha256(participant.encode('utf-8')).digest()
        # print(f'{fingerprint}\n\n')
        # fingerprint = hashlib.sha256(participant.encode('utf-8')).hexdigest()
        chat["participants"].append(b64encode(participant.encode()).decode('utf-8'))
        # print(f'Fingerprint: {chat["participants"]}\n\n')
        # print(f'Unhash: {[b64decode(user).decode() for user in chat["participants"]]}\n\n')

    
    chat = json.dumps(chat).encode('utf-8')
    

    iv = get_random_bytes(IV_LENGTH)
    
    sym_key = get_random_bytes(KEY_LENGTH)
    
    cipher_aes = AES.new(sym_key, AES.MODE_GCM, iv)
    cipher_chat, authTag = cipher_aes.encrypt_and_digest(chat)
    returned_cipher = cipher_chat + authTag
    # print(returned_cipher)
    
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

    
    
    return(returned_cipher, iv, symm_keys)

def decryptMessage(ciphertext, iv, enc_sym_keys):
    with open("./private_key.pem","r") as private_file:
        private_key = RSA.import_key(private_file.read(), passphrase="G40")
    
    decoded_enc_keys = [b64decode(key) for key in enc_sym_keys]
    cipher_rsa = PKCS1_OAEP.new(private_key, SHA256)
    auth_tag_len = 16 #16 bytes
    auth_tag = ciphertext[-auth_tag_len:]
    ciphertext = ciphertext[:-auth_tag_len]
    for enc_sym_key in decoded_enc_keys:
        try:
            decrypted_sym_key = cipher_rsa.decrypt(enc_sym_key)
            break
        except:
            continue
    try:
        cipher = AES.new(decrypted_sym_key, AES.MODE_GCM, iv)
        chat = cipher.decrypt_and_verify(ciphertext,auth_tag)
        chat = json.loads(chat.decode('utf-8'))
        chat["participants"] = [b64decode(user.encode('utf8')).decode() for user in chat["participants"]]
    except:
        return False
    return chat


#for testing this module seperately from the main program
if __name__ == "__main__":
    msg = "hello world"
    with open("./public_key.pem","r") as pub_file:
        pub_key = pub_file.read()
        
        # pub_key = pub_key.replace(pem_footer_pubk, "").replace("\n", "").strip()

    cipher_chat, nonce, enc_key = encryptMessage(msg,'kai','kai', pub_key)
    print(cipher_chat)

    deciphered = decryptMessage(cipher_chat, nonce, enc_key) 
    print(deciphered)
    
    with open("client_state.json","r") as client_state_json:
        client_state = json.load(client_state_json)
        all_users = client_state["online_users"]
    for user in all_users:
        server = user["address"]
        print(f"Address {server}:")
        for client in user["clients"]:
            print(f"    {client}")