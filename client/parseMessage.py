import json
from messageEncoder import encrypt_message




def PreProcessingOutMessage ():
    pass

# Take plain message as the input
def ParseOutMessage (message, type, subtype):

    parsedMessage = {}
    parsedMessage["type"] = type

    if type == "signed_data":
        with open('./client_state.json', 'r') as client_state:
            state_data = json.load(client_state)
        
        parsedMessage["data"] = {}
        parsedMessage["data"]["type"] = subtype
        
        # When connecting to the server: I think this is done
        if subtype == "hello":
            with open("./public_key.pem", 'r') as pub_k:
                public_key = pub_k.read()
            parsedMessage["data"]["public_key"] = public_key
            
        # No encrytion or encoding yet
        if subtype == "chat":
            parsedMessage["data"]["chat"] = {}
            parsedMessage["data"]["destination_server"] = []
            parsedMessage["data"]["iv"] = {}
            parsedMessage["data"]["symm_keys"] = []
            
            
            parsedMessage["data"]["chat"]["participants"] = []
            parsedMessage["data"]["chat"]["message"] = message
            
            
        if subtype == "public_chat":
            with open("./public_key.pem", 'r') as pub_k:
                public_key = pub_k.read()
            # Need encoder and SHA-256
            parsedMessage["data"]["sender"] = public_key
            parsedMessage["data"]["message"] = message
            
        
        # Random stuff for now
        parsedMessage["counter"] = state_data["counter"]
        state_data["counter"] += 1
        parsedMessage["signature"] = "signature"
        
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