import json
import hashlib
from base64 import b64encode, b64decode
from messageEncoder import encryptMessage, decryptMessage
from rsaSigner import rsaSign, rsaVerify 
from faker import Faker



SIGNATURE = ""
PUBLIC_KEY = ""
PRIVATE_KEY = ""
FINGERPRINT = ""


PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"


def PreProcessingOutMessage ():
    pass

# Take plain message as the input
def ParseOutMessage (message, msg_type, subtype, receiver, online_users):
    global PUBLIC_KEY
    global FINGERPRINT

    parsedMessage = {}
    parsedMessage["type"] = msg_type

    if msg_type == "signed_data":
        with open('./client_state.json', 'r') as client_state:
            state_data = json.load(client_state)
            FINGERPRINT = state_data["fingerprint"]
        
        parsedMessage["data"] = {}
        parsedMessage["data"]["type"] = subtype
        
        # When connecting to the server: I think this is done.
        # Load the public key.
        if subtype == "hello":
            with open("./public_key.pem", 'r') as pub_k:
                public_key = pub_k.read()
                PUBLIC_KEY = public_key
            # Parse public key and generate signature
            parsedMessage["data"]["public_key"] = PUBLIC_KEY
            
            # what does this section do?
            # key_bytes = b64decode(PUBLIC_KEY)
            # key_bytes = PUBLIC_KEY.encode('ascii')
            # SIGNATURE = hashlib.sha256(key_bytes).digest()
            # SIGNATURE = b64encode(SIGNATURE).decode('utf-8')

            
            
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
            
            receiver.insert(0, "")
            
            with open("./client_state.json", 'r') as file:
                client_state = json.load(file)
                recipients = client_state["online_users"][0]["clients"]
                try:
                    recipients.remove(PUBLIC_KEY)
                except:
                    pass
                recipients.insert(0, PUBLIC_KEY)
            cipher_chat, iv, sym_key = encryptMessage(message,recipients,recipients)
            parsedMessage["data"]["chat"] = b64encode(cipher_chat).decode('utf8')
            parsedMessage["data"]["iv"] = b64encode(iv).decode('utf8')
            parsedMessage["data"]["symm_keys"] = sym_key
            # print(parsedMessage)
            
            
            
        if subtype == "public_chat":
            parsedMessage["data"]["sender"] = FINGERPRINT
            parsedMessage["data"]["message"] = message
            
        # Random stuff for now
        parsedMessage["counter"] = state_data["counter"]
        state_data["counter"] += 1
        # Need base64
        
        # print(type(parsedMessage["data"]))
        data_json_string = json.dumps(parsedMessage["data"])
        data_json_string += str(parsedMessage["counter"])
        SIGNATURE = rsaSign(data_json_string)
        parsedMessage["signature"] = b64encode(SIGNATURE).decode()
        # parsedMessage["signature"] = "Kai"
        
        with open('./client_state.json', 'w') as client_state_dump:
            json.dump(state_data, client_state_dump, indent=4)
        
        with open('./client_state.json', 'w') as client_state_dump:
            json.dump(state_data, client_state_dump, indent=4)
            
    elif msg_type == "client_list_request":
        # parsedMessage["type"] = type
        pass

                
    
    parsedJsonMessage = json.dumps(parsedMessage).encode('utf-8')
    
    
    return parsedJsonMessage

def ParseInMessage (message):
    # print(f'mess::::::::::: {message}')
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    # print(parsed_message)

    msg_type = parsed_message['type']
    
    if parsed_message["type"] == "signed_data":
        msg_type += f"_{parsed_message['data']['type']}"
        if parsed_message["data"]["type"] == "chat":
            try:
                ciphertext = b64decode(parsed_message["data"]["chat"])
                iv = b64decode(parsed_message["data"]["iv"])
                enc_key =  parsed_message["data"]["symm_keys"]
            except Exception as e:
                raise ValueError(e)
            
            message_info = {}
            try: 
                    chat = decryptMessage(ciphertext, iv, enc_key)
                    with open('./client_state.json', 'r') as client_state:
                        state_data = json.load(client_state)
                    message_info["message"] = chat["message"]
                    for p in chat["participants"]:
                        if p not in state_data["NS"]:
                            state_data["NS"][p] ={}
                            state_data["NS"][p]["name"] = Faker().name()
                            state_data["NS"][p]["color"] = Faker().hex_color()
                            
                    with open('./client_state.json', 'w') as fout:
                        json.dump(state_data, fout, indent=4)
                        
                    for fp in state_data["NS"]:
                        if fp == chat["participants"][0]:
                            message_info["sender"] = state_data["NS"][fp]["name"]            
                            message_info["color"] = state_data["NS"][fp]["color"]            
            except Exception as e:
                raise ValueError(e)
            return message_info, msg_type
            # try:
            #     if (rsaVerify(chat, signature, public_key)):
            #         verified_chat = chat
            # except Exception as e:
            #     raise ValueError(e)
            # return verified_chat
    
    if parsed_message["type"] == "client_list":
        with open("client_state.json","r") as client_state_json:
            client_state = json.load(client_state_json)
        
        
        client_state["online_users"] = parsed_message["servers"]
        
        with open("client_state.json","w") as client_state_json:
            json.dump(client_state, client_state_json, indent=4)

    return parsed_message, msg_type
