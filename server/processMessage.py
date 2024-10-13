# import json
# import uuid
# from eventLogger import eventLogger
# from base64 import b64encode, b64decode
# from rsaSigner import rsaSign, rsaVerify


# def ValidateMessage(recv_counter, cached_counter):
    
#     if recv_counter <= cached_counter:
#         return False
    
#     return True

# def ProcessInMessage(message, client_id):
    
#     status = 1
#     log_message = "Message received."
#     # return_message = ""      
#     sent_from = client_id
#     fr_ent = "c"
    
#     parsed_message = message.decode('utf-8')
#     parsed_message = json.loads(parsed_message)
    
#     type = parsed_message["type"]
    
    
#     with open("./state.json", 'r') as server_state_read:
#         server_state = json.load(server_state_read)
    
    
#     if type == "signed_data":
#         if sent_from == "-1" and parsed_message["data"]["type"] != "hello":
#             return None, None, None,None, None
        
#         if parsed_message["data"]["type"] != "hello":
#             sender_pub_k = server_state["clients"][client_id]["public_key"]
#             print(f"sender_pub_k: {sender_pub_k}")
#             data_json_string = json.dumps(parsed_message["data"]) + str(parsed_message["counter"])
#             print(f"data_json_string: {data_json_string}")
#             signature = b64decode(parsed_message["signature"].encode())
#             print(f"Sign: {signature}")
#             is_verified = rsaVerify(data_json_string, signature, sender_pub_k)

#             print(f"Origin: {is_verified}")
        
#         if sent_from != "-1" and ValidateMessage(parsed_message["counter"], server_state["clients"][sent_from]["counter"]) == False:
#             return None, None, None, None, None
        
        
#         # Parser for chat
#         if parsed_message["data"]["type"] == "chat":
#             # print("recv")
#             type += "_chat"
#             # encoded_chat = parsed_message["data"]["chat"]
#             # print(parsed_message)
#             # print(encoded_chat)
            
                
#         # Parser for public_chat
#         elif parsed_message["data"]["type"] == "public_chat":
#             type += "_public_chat"
#             encoded_chat = parsed_message["data"]["message"]
#             # pass
        
        
#         # Parser for server connection
#         elif parsed_message["data"]["type"] == "hello":
#             type += "_hello"
#             data = parsed_message["data"]
                
#             client_found_in_server = False
#             for client_id in server_state["clients"]:
#                 if server_state["clients"][client_id]['public_key'] == data["public_key"]:
#                     # print(f"Existing client {client_id}")
#                     server_state['clients'][client_id]["counter"] = parsed_message["counter"]
#                     client_found_in_server = True
#                     sent_from = client_id
#                     # break
                    
            
            
#             if not client_found_in_server:
#                 while True:
#                     new_client_id = str(uuid.uuid4())
#                     if new_client_id not in server_state["clients"]:
#                         server_state["clients"][new_client_id] = {}
#                         server_state["clients"][new_client_id]["counter"] = parsed_message["counter"]
#                         server_state["clients"][new_client_id]["public_key"] = data["public_key"]
#                         sent_from = new_client_id
#                         break

#             status = 1 
#             log_message = f"Connection Establised"     
        
#         elif parsed_message["data"]["type"] == "server_hello":
#             type += "_server_hello"
#             fr_ent = "s"
            
#     elif type == "client_list_request":
#         type = "client_list_request"
#         log_message = "Received online user list request"
#         # print(parsed_message["type"])
#     elif type == "client_update_request":
#         fr_ent = "s"
#         pass
#     elif type == "client_update":
#         fr_ent = "s"
#         pass
#     else:
#         print(f"Message has invalid type {parsed_message["type"]}")
    
    
#     with open("./state.json", 'w') as server_state_write:
#         json.dump(server_state, server_state_write, indent=4)  
    
#     return type, status, log_message, sent_from, parsed_message




# def AssembleOutwardMessage (msg_type, subtype, message):
#     outward_message = {}
#     outward_message["type"] = msg_type
    
#     with open("./state.json", 'r') as server_state_read:
#         server_state = json.load(server_state_read)
    
#     if msg_type == "signed_data":
#         outward_message["data"] = {}
#         outward_message["data"]["type"] = subtype

#         if subtype == "server_hello":
#             outward_message["data"]["sender"] = message
#             outward_message["counter"] = server_state["counter"]
            
        
#         if subtype == "chat" or subtype == "public_chat":
#             # try:
#             #     in_counter = message["counter"]
#             #     in_signature = b64decode(message["signature"])
#             #     out_counter = server_state["counter"]
#             #     print(in_counter)
#             #     out_signature = f"{in_signature[:-len(str(in_counter))]}{str(out_counter)}"
                
#             #     outward_message["counter"] = out_counter
#             #     # outward_message["signature"] = b64encode(out_signature)
#             #     outward_message["signature"] = out_signature
#             #     print(message)
#             #     outward_message["data"] = message["data"]
#             # except Exception as e:
#             #     print(f"Incorrect message format: {e}")
#             outward_message["data"] = message["data"]
#             outward_message["counter"] = message["counter"]
#             # outward_message["signature"] = message["signature"]
#             # print(outward_message["signature"])
        
#         server_state["counter"] += 1
            
            
#     elif msg_type == "client_list":
#         outward_message["servers"] = message
        
#     elif msg_type == "client_update_request":
#         pass
    
#     elif msg_type == "client_update":
#         outward_message["clients"] = message
    
#     with open("./state.json", 'w') as server_state_write:
#         json.dump(server_state, server_state_write, indent=4) 
    
#     outward_message_json = json.dumps(outward_message).encode('utf-8')
#     return outward_message_json


# def ProcessOnlineUsersList(internal_online_users, masterserver_address, external_online_users):
#     client_list = []
    
#     online_users_in_server = {}
#     online_users_in_server["clients"] = []
    
#     online_users_in_server["address"] = masterserver_address
#     for id in internal_online_users:
#         online_users_in_server["clients"].append(internal_online_users[id]["public_key"])
            
#     client_list.append(online_users_in_server)
    
#     for server in external_online_users:
#         external_client = {}
#         external_client["address"] = server
#         external_client["clients"] = external_online_users[server]
        
#         client_list.append(external_client)
        
#     return client_list

import json
import uuid
from base64 import b64encode, b64decode
from rsaSigner import rsaSign, rsaVerify


def ValidateMessage(recv_counter, cached_counter):
    
    if recv_counter <= cached_counter:
        return False
    
    return True

def ProcessInMessage(message, client_id, from_server: bool):
    
    status = 1
    log_message = "Message received."
    sent_from = client_id
    
    parsed_message = message.decode('utf-8')
    parsed_message = json.loads(parsed_message)
    
    type = parsed_message['type']
    
    
    with open("./state.json", 'r') as server_state_read:
        server_state = json.load(server_state_read)
    
    
    if type == "signed_data":
        if sent_from == "-1" and not from_server and parsed_message['data']['type'] != "hello":
            return None, 0, None,None, None
        
        # if not from_server and parsed_message['data']['type'] != "server_hello":
        #     return None, 0, None,None, None
        
        if sent_from != "-1" and not from_server\
            and ValidateMessage(parsed_message['counter'], server_state['clients'][sent_from]['counter']) == False:
            return None, 0, None, None, None
        
        decoded_signature =  b64decode(parsed_message['signature'])
        recv_counter = parsed_message['counter']
        
        # Parser for chat
        if parsed_message['data']['type'] == "chat":
            type += "_chat"

        # Parser for public_chat
        elif parsed_message['data']['type'] == "public_chat":
            type += "_public_chat"
            encoded_chat = parsed_message['data']['message']
            # pass
        
        
        # Parser for server connection
        elif parsed_message['data']['type'] == "hello":
            type += "_hello"
            data = parsed_message['data']

            
                
            client_found_in_server = False
            for client_id in server_state['clients']:
                if server_state['clients'][client_id]['public_key'] == data['public_key']:
                    # print(f"Existing client {client_id}")
                    server_state['clients'][client_id]['counter'] = recv_counter
                    client_found_in_server = True
                    sent_from = client_id
                    # break
                    
            if not client_found_in_server:
                while True:
                    new_client_id = str(uuid.uuid4())
                    if new_client_id not in server_state['clients']:
                        server_state['clients'][new_client_id] = {}
                        server_state['clients'][new_client_id]['counter'] = recv_counter
                        server_state['clients'][new_client_id]['public_key'] = data['public_key']
                        sent_from = new_client_id
                        break
                    
            # Verify signature
            try:
                data_json_string = json.dumps(parsed_message['data'])
                data_json_string += str(recv_counter)
                
                if (rsaVerify(data_json_string, decoded_signature, data['public_key']) != True):
                    print("Not verified")
                    return None, 0, None, None, None
                print("verified")
            except Exception as e:
                print(f"Not verified: {e}")
                return None, 0, None, None, None
            
            status = 1 
            log_message = f"Connection Establised"     
        
        elif parsed_message['data']['type'] == "server_hello": # and from_server:
            type += "_server_hello"
            
            # Verify signature
            try:
                data_json_string = json.dumps(parsed_message['data'])
                data_json_string += str(recv_counter)
                
                    
                send_server_pubk = ""
                # Retrieve public key from neighbour list 
                for neighbour in server_state['neighbours']:
                    if neighbour['address'] == parsed_message['data']['sender']:
                        send_server_pubk = neighbour['public_key']
                
                # Neighbour not found => Invalid
                if send_server_pubk == "":
                    return None, 0, None, None, None
        
                if (rsaVerify(data_json_string, decoded_signature, send_server_pubk) != True):
                    print("Not verified")
                    return None, 0, None, None, None
                print("verified")
            except Exception as e:
                print(f"Not verified: {e}")
                return None, 0, None, None, None
            
            
    elif type == "client_list_request" and sent_from != "-1":
        log_message = "Received online user list request"
        # print(parsed_message['type'])
    elif type == "client_update_request":# and from_server:
        log_message = "Received online user list update request"
        # pass
    elif type == "client_update":# and from_server:
        log_message = "Received online user list update"
        # pass
    else:
        print(f"Message has invalid type {parsed_message['type']}")
    
    
    with open("./state.json", 'w') as server_state_write:
        json.dump(server_state, server_state_write, indent=4)  
    
    return type, status, log_message, sent_from, parsed_message




def AssembleOutwardMessage (msg_type, subtype, message):
    outward_message = {}
    outward_message['type'] = msg_type
    
    with open("./state.json", 'r') as server_state_read:
        server_state = json.load(server_state_read)
    
    if msg_type == "signed_data":
        outward_message['data'] = {}
        outward_message['data']['type'] = subtype

        if subtype == "server_hello":
            outward_message['data']['sender'] = message
            outward_message['counter'] = server_state['counter']
            
            #  Sign server-hello
            data_json_string = json.dumps(outward_message['data'])
            data_json_string += str(outward_message['counter'])
            out_signature = rsaSign(data_json_string)
            outward_message['signature'] = b64encode(out_signature).decode()
            print(outward_message['signature'] )   
            
        
        if subtype == "chat" or subtype == "public_chat":
            pass
            
            
    elif msg_type == "client_list":
        outward_message['servers'] = message
        
    elif msg_type == "client_update_request":
        pass
    
    elif msg_type == "client_update":
        outward_message['clients'] = message[0]['clients']
    
    with open("./state.json", 'w') as server_state_write:
        json.dump(server_state, server_state_write, indent=4) 
    

    
    outward_message_json = json.dumps(outward_message).encode('utf-8')
    return outward_message_json


def ProcessOnlineUsersList(internal_online_users, masterserver_address, external_online_users):
    client_list = []
    
    online_users_in_server = {}
    online_users_in_server['clients'] = []
    
    online_users_in_server['address'] = masterserver_address
    for id in internal_online_users:
        online_users_in_server['clients'].append(internal_online_users[id]['public_key'])
            
    client_list.append(online_users_in_server)
    
    for server in external_online_users:
        external_client = {}
        external_client['address'] = server
        external_client['clients'] = external_online_users[server]
        
        client_list.append(external_client)
        
    return client_list

