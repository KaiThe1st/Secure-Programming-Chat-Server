import json
import uuid
from eventLogger import eventLogger

def ProcessInMessage(message, client_id):
    
    status = 1
    log_message = "Message received."
    # return_message = ""      
    sent_from = client_id
    
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    
    type = parsed_message["type"]
    
    
    with open("./state.json", 'r') as server_state_read:
        server_state = json.load(server_state_read)
    
    
    if type == "signed_data":
        
        # Parser for chat
        if parsed_message["data"]["type"] == "chat":
            
            # print("recv")
            type += "_chat"
            # encoded_chat = parsed_message["data"]["chat"]
            # print(parsed_message)
            # print(encoded_chat)
            
                
        # Parser for public_chat
        elif parsed_message["data"]["type"] == "public_chat":
            type += "_public_chat"
            encoded_chat = parsed_message["data"]["chat"]
            # pass
        
        
        # Parser for server connection
        elif parsed_message["data"]["type"] == "hello":
            type += "_hello"
            data = parsed_message["data"]
                
            client_found_in_server = False
            for client_id in server_state["clients"]:
                if server_state["clients"][client_id]['public_key'] == data["public_key"]:
                    # print(f"Existing client {client_id}")
                    server_state['clients'][client_id]["counter"] = parsed_message["counter"]
                    client_found_in_server = True
                    sent_from = client_id
                    # break
                    
            
            
            if not client_found_in_server:
                while True:
                    new_client_id = str(uuid.uuid4())
                    if new_client_id not in server_state["clients"]:
                        server_state["clients"][new_client_id] = {}
                        server_state["clients"][new_client_id]["counter"] = parsed_message["counter"]
                        server_state["clients"][new_client_id]["public_key"] = data["public_key"]
                        sent_from = new_client_id
                        break

            status = 1 
            log_message = f"Connection Establised"     
        
        elif parsed_message["data"]["type"] == "server_hello":
            type += "_server_hello"
            
    elif type == "client_list_request":
        type = "client_list_request"
        log_message = "Received online user list request"
        # print(parsed_message["type"])
    elif type == "client_update_request":
        pass
    elif type == "client_update":
        pass
    else:
        print(f"Message has invalid type {parsed_message["type"]}")
    
    
    with open("./state.json", 'w') as server_state_write:
        json.dump(server_state, server_state_write, indent=4)  
    
    return type, status, log_message, sent_from, parsed_message




def AssembleOutwardMessage (type, subtype, message):
    outward_message = {}
    outward_message["type"] = type
      
    if type == "signed_data":
        outward_message["data"]["type"] = subtype

        if subtype == "server_hello":
            outward_message["sender"] = message
            
    elif type == "client_list":
        outward_message["servers"] = message
        
    elif type == "client_update_request":
        pass
    
    elif type == "client_update":
        outward_message["clients"] = message
    
    outward_message_json = json.dumps(outward_message).encode('utf-8')
    return outward_message_json


def ProcessOnlineUsersList(internal_online_users, external_online_users):
    client_list = []
    
    for server in internal_online_users:
        online_users_in_server = {}
        online_users_in_server["address"] = server
        online_users_in_server["clients"] = []
        for client in internal_online_users[server]:
            online_users_in_server["clients"].append(internal_online_users[server][client]["public_key"])
            
        client_list.append(online_users_in_server)
    
    for server in external_online_users:
        external_client = {}
        external_client["address"] = server
        external_client["clients"] = external_online_users[server]
        
        client_list.append(external_client)
        
    return client_list

