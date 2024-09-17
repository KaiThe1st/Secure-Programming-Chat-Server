import json
import uuid
from eventLogger import eventLogger

def ProcessInMessage(message, client_id):
    
    
    type = "received"
    status = 1
    log_message = "Message received."
    return_message = ""      
    sent_from = client_id
    
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    
    with open("./state.json", 'r') as server_state_read:
        server_state = json.load(server_state_read)
    
    if parsed_message["type"] == "signed_data":
        
        # Parser for chat
        if parsed_message["data"]["type"] == "chat":
            
            # print("recv")
            type = "signed_data_chat"
            encoded_chat = parsed_message["data"]["chat"]
            print(parsed_message)
            print(encoded_chat)
            
                
        # Parser for public_chat
        if parsed_message["data"]["type"] == "public_chat":
            type = "signed_data_public_chat"
            encoded_chat = parsed_message["data"]["chat"]
            # pass
        
        
        # Parser for server connection
        if parsed_message["data"]["type"] == "hello":
            type = "signed_data_hello"
            data = parsed_message["data"]
                
            client_found_in_server = False
            for client_id in server_state["clients"]:
                if server_state["clients"][client_id]['public_key'] == data["public_key"]:
                    # print(f"User is {client_id}")
                    server_state['clients'][client_id]["counter"] = parsed_message["counter"]
                    client_found_in_server = True
                    sent_from = client_id
                    
            
            
            if not client_found_in_server:
                while True:
                    client_id = str(uuid.uuid4())
                    if client_id not in server_state["clients"].keys():
                        server_state["clients"][client_id] = {}
                        server_state["clients"][client_id]["counter"] = parsed_message["counter"]
                        server_state["clients"][client_id]["public_key"] = data["public_key"]
                        sent_from = client_id
                        break

            status = 1 
            log_message = f"Connection Establised"      

            
    elif parsed_message["type"] == "client_list_request":
        type = "client_list_request"
        log_message = "Received online user list request"
        # print(parsed_message["type"])
    else:
        print(f"Message has invalid type {parsed_message["type"]}")
    
    
    with open("./state.json", 'w') as server_state_write:
        json.dump(server_state, server_state_write, indent=4)  
    
    return type, status, log_message, sent_from




def AssembleOutwardMessage (type, message):
    outward_message = {}
    outward_message["type"] = type
    
    if type == "client_list":
        outward_message["servers"] = [
            {
                "address": "<Address of server>",
                "clients": [
                    "<Exported RSA public key of client>",
                ]
            },
        ]
        

    if type == "signed_data_chat":
        outward_message["data"] = message
    
    outward_message_json = json.dumps(outward_message).encode('utf-8')
    return outward_message_json


def ProcessOnlineUsersList(innerdata, master_server, outterdata):
    client_list = []
    
    # Intra server online users
    intra_server_onl_u = {}
    intra_server_onl_u['address'] = master_server["ip"] + ":" + master_server["port"]
    intra_server_onl_u['clients'] = []
    
    
    for intra_client in innerdata:
        intra_server_onl_u['clients'].append(master_server["clients"][intra_client]["public_key"])
        
    # Need Inter server online users logic here
    # inter_server_onl_u = {}
    
    
    client_list.append(intra_server_onl_u)
    # client_list.append(inter_server_onl_u)
        
    return client_list

