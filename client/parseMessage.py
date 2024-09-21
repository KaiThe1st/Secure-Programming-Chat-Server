import json
import hashlib
from base64 import b64encode, b64decode
from messageEncoder import encryptMessage


SIGNATURE = ""
PUBLIC_KEY = ""
PRIVATE_KEY = ""


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
            pem_header_pubk = "-----BEGIN PUBLIC KEY-----"
            pem_footer_pubk = "-----END PUBLIC KEY-----"
            PUBLIC_KEY = public_key.replace(pem_header_pubk, "").replace(pem_footer_pubk, "").replace("\n", "").strip()
            key_bytes = b64decode(PUBLIC_KEY)
            SIGNATURE = hashlib.sha256(key_bytes).digest()
            SIGNATURE = b64encode(SIGNATURE).decode('utf-8')
            
            parsedMessage["data"]["public_key"] = PUBLIC_KEY
            
            
        # No encrytion or encoding yet
        if subtype == "chat":
            parsedMessage["data"]["chat"] = {}
            parsedMessage["data"]["destination_server"] = []
            parsedMessage["data"]["iv"] = ""
            parsedMessage["data"]["symm_keys"] = []
            
            
            parsedMessage["data"]["chat"]["participants"] = []
            
            receiver.insert(0, SIGNATURE)
            cipher_chat, authTag, iv, sym_key = encryptMessage(message, receiver, online_users)
            parsedMessage["data"]["chat"] = str(cipher_chat)
            parsedMessage["data"]["iv"] = str(b64encode(iv))
            print(parsedMessage)
            
            
            
        if subtype == "public_chat":
            parsedMessage["data"]["sender"] = SIGNATURE
            parsedMessage["data"]["message"] = message
            
        
        # Random stuff for now
        parsedMessage["counter"] = state_data["counter"]
        state_data["counter"] += 1
        # Need base64
        parsedMessage["signature"] = f"{parsedMessage['data']}{parsedMessage['counter']}"
        
        with open('./client_state.json', 'w') as client_state_dump:
            json.dump(state_data, client_state_dump, indent=4)
            
    elif type == "client_list_request":
        # parsedMessage["type"] = type
        pass

                
    
    parsedJsonMessage = json.dumps(parsedMessage).encode('utf-8')
    
    
    return parsedJsonMessage

def ParseInMessage (message) :
    # print(f'mess::::::::::: {message}')
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    
    return parsed_message