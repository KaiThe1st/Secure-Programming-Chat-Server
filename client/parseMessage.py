import json
import hashlib
from base64 import b64encode, b64decode
from messageEncoder import encryptMessage, decryptMessage
from rsaSigner import rsaSign, rsaVerify 


SIGNATURE = ""
PUBLIC_KEY = ""
PRIVATE_KEY = ""

PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"


def PreProcessingOutMessage ():
    pass

# Take plain message as the input
def ParseOutMessage (message, type, subtype, receiver, online_users):
    global SIGNATURE
    

    parsedMessage = {}
    parsedMessage["type"] = type

    if type == "signed_data":
        with open('./client_state.json', 'r') as client_state:
            state_data = json.load(client_state)
        
        parsedMessage["data"] = {}
        parsedMessage["data"]["type"] = subtype
        
        # When connecting to the server: I think this is done.
        # Load the public key.
        if subtype == "hello":
            with open("./public_key.pem", 'r') as pub_k:
                public_key = pub_k.read()
            # Parse public key and generate signature
            PUBLIC_KEY = public_key.replace(PEM_FOOTER_PUBK, "").replace(PEM_HEADER_PUBK, "").replace("\n", "").strip()
            parsedMessage["data"]["public_key"] = PUBLIC_KEY
            
            # what does this section do?
            key_bytes = b64decode(PUBLIC_KEY)
            SIGNATURE = hashlib.sha256(key_bytes).digest()
            SIGNATURE = b64encode(SIGNATURE).decode('utf-8')

            
            
        # No encrytion or encoding yet
        if subtype == "chat":
            parsedMessage["data"]["destination_servers"] = []
            parsedMessage["data"]["iv"] = ""
            parsedMessage["data"]["symm_keys"] = []
            parsedMessage["data"]["chat"] = {}
            parsedMessage["data"]["client_info"] = {}
            parsedMessage["data"]["client_info"]["client_id"] = []
            parsedMessage["data"]["client_info"]["server_id"] = []
            parsedMessage["time-to-die"] = [] # UTC timestamp (1 minute)
            
            # parsedMessage["authTag"] = "" # is necessary?
            
            parsedMessage["data"]["chat"]["participants"] = []
            
            receiver.insert(0, SIGNATURE)
            
            with open("./public_key.pem", 'r') as pub_k:
                public_key = pub_k.read()
            cipher_chat, iv, sym_key = encryptMessage(message, receiver, online_users, public_key)
            parsedMessage["data"]["chat"] = b64encode(cipher_chat).decode('utf8')
            parsedMessage["data"]["iv"] = b64encode(iv).decode('utf8')
            parsedMessage["data"]["symm_keys"] = b64encode(sym_key).decode('utf8')
            print(parsedMessage)
            
            
            
        if subtype == "public_chat":
            parsedMessage["data"]["sender"] = SIGNATURE
            parsedMessage["data"]["message"] = message
            
        
        # Random stuff for now
        parsedMessage["counter"] = state_data["counter"]
        state_data["counter"] += 1
        # Need base64
        parsedMessage["signature"] = f"{SIGNATURE}{parsedMessage['counter']}"
        
        with open('./client_state.json', 'w') as client_state_dump:
            json.dump(state_data, client_state_dump, indent=4)
            
    elif type == "client_list_request":
        # parsedMessage["type"] = type
        pass

                
    
    parsedJsonMessage = json.dumps(parsedMessage).encode('utf-8')
    
    
    return parsedJsonMessage

def ParseInMessage (message):
    # print(f'mess::::::::::: {message}')
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    # print(parsed_message)


    
    if parsed_message["type"] == "signed_data":
        if parsed_message["data"]["type"] == "chat":
            try:
                ciphertext = b64decode(parsed_message["data"]["chat"])
                iv = b64decode(parsed_message["data"]["iv"])
                enc_key =  b64decode(parsed_message["data"]["symm_keys"])
            except Exception as e:
                raise ValueError(e)
            
            try: 
                chat = decryptMessage(ciphertext, iv, enc_key)
            except Exception as e:
                raise ValueError(e)
        
            return chat
    
    return parsed_message