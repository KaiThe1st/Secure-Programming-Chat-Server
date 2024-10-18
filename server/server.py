# Code by Group UG40
# Nathan Dang (a1794954@adelaide.edu.au)
# Haydn Gaetdke (a1860571@adelaide.edu.au)
# Quoc Khanh Duong (a1872857@adelaide.edu.au)
# Dang Hoan Nguyen (a1830595@adelaide.edu.au)

import asyncio
import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json
import os
# import logging
import socket
import re
from datetime import datetime
import hashlib
# logging.basicConfig(level=logging.DEBUG)

from aiohttp import web, ClientConnectorError, WSServerHandshakeError

internal_online_users = {
    
}

IP = socket.gethostbyname(socket.gethostname())

if (not(os.path.isfile("private_key.pem") and os.path.isfile("public_key.pem"))):
    raise ValueError("Key not found. Please run createFile.py")
if (not(os.path.isfile("state.json"))):
    raise ValueError("State file not found. Please run createFile.py and populate neighbour informations")


with open("./state.json", 'r') as server_state:
    state = json.load(server_state)
    state['ip'] = IP
    
print(f'I am : {IP}') # For ease when connecting to server from a different machine

SELF_ADDRESS = f'{state['ip']}:{state['port']}'
NEIGHBOURS = state['neighbours']
ONLINE_NEIGHBOURS = {}
ONLINE_NEIGHBOURS_SENT = []

MAX_FILE_SIZE = 1024 * 1024 * 3 # 3MB
MAX_MESSAGE_LENGTH = 140
external_online_users = {}

async def server_startup(app):
    for idx in range(len(NEIGHBOURS)):
        
        if NEIGHBOURS[idx]['address'].strip() == SELF_ADDRESS or NEIGHBOURS[idx]['address'].strip() in ONLINE_NEIGHBOURS_SENT: # or NEIGHBOURS[idx]['address'].strip() in ONLINE_NEIGHBOURS:
            continue
        
        ONLINE_NEIGHBOURS_SENT.append(NEIGHBOURS[idx]['address'].strip())
        distant_address = "ws://" + NEIGHBOURS[idx]['address'] + "/"
        
        asyncio.create_task(init_server_connection(distant_address, idx))

async def init_server_connection(distant_address, idx):
    async with websockets.connect(distant_address, ping_interval=10) as server_websocket:
        try:
            server_hello_mess = AssembleOutwardMessage("signed_data", "server_hello", SELF_ADDRESS)
            print(server_hello_mess)
            await server_websocket.send(server_hello_mess)
            
            client_update_request_mess = AssembleOutwardMessage("client_update_request", "", "")
            print(client_update_request_mess)
            await server_websocket.send(client_update_request_mess)
            if distant_address not in ONLINE_NEIGHBOURS:
                ONLINE_NEIGHBOURS[distant_address] = {}
            ONLINE_NEIGHBOURS[distant_address]['socket'] = server_websocket
            ONLINE_NEIGHBOURS[distant_address]['counter'] = NEIGHBOURS[idx]['counter']
            
            while True:
                await asyncio.sleep(10)
                continue
        except Exception as e:
            print(f"An error occurred: {e}")
            


# WebSocket server handler
async def ws_handler(request):
    websocket = web.WebSocketResponse(heartbeat=30)
    await websocket.prepare(request) 
    
    # await init_server_connection()
       
    
    async for msg in websocket:
        global internal_online_users
        
        print("_________________________")
        print(msg)
        
        from_user = "-1"
        from_server = 0
        
        try:

            message = msg.data

            # Identify the user who sent the message
            # By comaparing the sending websocket object against the recorded websocket object
            # for server_address in internal_online_users:
            for id in internal_online_users:
                if internal_online_users[id]['socket'] == websocket:
                    from_user = id
                    break



            if from_user == "-1":
                # if request is not None:
                    
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip.strip()}"
                print(distant_address)
            
            # Process the Message
            # type: a message type as defined in the protocol document in the form f"{type}_{sub_type}"
            # status : 
            # sent_from: user_id
            # log_message: recording the event
            
            type, status, log_message, sent_from, parsed_message = ProcessInMessage(message, from_user, from_server)
            
            print(type)
            
            if type == None:
                continue
            
            if sent_from != "-1" or from_server == 1:
                await websocket.close(code=4000, reason="Limited one client on a host")
            
            eventLogger(type, status, sent_from, log_message)
            
            # HANDLE HELLO
            if type == "signed_data_hello" and from_server == 0 and sent_from != "-1":
                # prevent multiconnection on a single client
                if sent_from in internal_online_users \
                    and internal_online_users[sent_from]['socket'] is not websocket:
                        # await web.Response(text="Access denied.", status=403)
                        continue
                
                if sent_from not in internal_online_users:
                    internal_online_users[sent_from] = {}
                    internal_online_users[sent_from]['socket'] = websocket
                    internal_online_users[sent_from]['public_key'] = parsed_message['data']['public_key']
                    
                    # Process an updated list of users
                    all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                    client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)
                    
                    # Send updated client list to all other clients apart from the sender
                    for client_id in internal_online_users:
                        if internal_online_users[client_id]['socket'] != websocket:
                            try:
                                await internal_online_users[client_id]['socket'].send(client_list_res_message)
                            except AttributeError:
                                await internal_online_users[client_id]['socket'].send_str(client_list_res_message)
                                
                    # Send updated internal client list to all online neighbour servers
                    internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                    client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                    for server_address in ONLINE_NEIGHBOURS:
                        try:
                            await ONLINE_NEIGHBOURS[server_address]['socket'].send(client_update_res_message)
                        except AttributeError:
                            await ONLINE_NEIGHBOURS[server_address]['socket'].send_str(client_update_res_message)
                        except Exception as e:
                            print(f"Not exist socket: {e}")
                            try:
                                async with websockets.connect(server_address) as websocket:
                                    websocket.send(client_update_res_message)
                            except Exception as e:
                                print(f"Failed to establish connection {e}")
                    
                    
                    await websocket.send_str("Connection established")

            # HANDLE SERVER HELLO
            elif type == "signed_data_server_hello" and from_server == 1:
                sending_server = parsed_message['data']['sender']
                ONLINE_NEIGHBOURS[sending_server]['socket'] = websocket
                
                
            # HANDLE REQUEST FOR ONLINE CLIENTS
            elif type == "client_list_request" and from_server == 0 and sent_from != "-1":
                
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_mess = AssembleOutwardMessage("client_list", "", all_online_users)
                await websocket.send_str(client_list_res_mess)

            
            # HANDLE REQUEST FOR CLIENT UPDATE FROM SERVERS
            elif type == "client_update_request": # and from_server == 1:
                internal_clients = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_mess = AssembleOutwardMessage("client_update", "", internal_clients)
                
                try:    
                    await websocket.send_str(client_update_res_mess)
                except AttributeError:
                    await websocket.send(client_update_res_mess)

            
            # HANDLE CLIENT UPDATE
            elif type == "client_update":
                
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip.strip()}:{distant_port}"
                external_online_users[distant_address] = parsed_message['clients']
                
            
                # Generate message to send to clients
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)    
                # Send the updated client list to all online clients connected to this server
                
                for client_id in internal_online_users:
                    if internal_online_users[client_id]['socket'] != websocket:
                        await internal_online_users[client_id]['socket'].send_str(client_list_res_message)
                
            # HANDLE CHAT
            elif type == "signed_data_chat": # and sent_from != "-1":
                    
                # Send the message to all online neighbour servers
                if from_server == 0:
                    for neighbour in ONLINE_NEIGHBOURS:
                        # if neighbour in parsed_message['data']['destination_servers'] and prev != neigbour:
                        try:
                            await ONLINE_NEIGHBOURS[neighbour]['socket'].send(message)
                        except AttributeError:
                            await ONLINE_NEIGHBOURS[neighbour]['socket'].send_str(message)
                        except Exception as e:
                            print(f"Not exist socket: {e}")
                            try:
                                async with websockets.connect(neighbour) as websocket:
                                    websocket.send(message)
                            except Exception as e:
                                print(f"Failed to establish connection {e}")

                # Send the message to all online clients
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]['socket']
                    if socket != websocket:
                        await socket.send_str(message) 
                    
                        
            # HANDLE PUBLIC CHAT
            elif type == "signed_data_public_chat": # and sent_from != "-1":
                # Send message to neighbour servers when the message is from a client    
                if from_server == 0:
                    for neighbour in ONLINE_NEIGHBOURS:
                        try:
                            await ONLINE_NEIGHBOURS[neighbour]['socket'].send(message)
                        except AttributeError:
                            await ONLINE_NEIGHBOURS[neighbour]['socket'].send_str(message)
                        except Exception as e:
                            print(f"Not exist socket: {e}")
                            try:
                                async with websockets.connect(neighbour) as websocket:
                                    websocket.send(message)
                            except Exception as e:
                                print(f"Failed to establish connection {e}")
                
                # Send the message to all online clients connected to this master server
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]['socket']
                    if socket != websocket:
                        await socket.send_str(message) 
                        
            else:
                await websocket.send_str(f'ACK: {log_message}')
            
        except Exception as e:
            print("=======")
            print(e)
            print("=======")
            
            
            
    # print("WebSocket connection closed")
    # When one client is closing the connection
    disconnected_user = "unknown"
    for online_user_id in internal_online_users:
        if (internal_online_users[online_user_id]['socket'] == websocket):
            disconnected_user = online_user_id
            
            del internal_online_users[online_user_id]
            
            try:
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)
                print(client_list_res_message)
                
                # Send updated client list to all clients apart from the sender
                for client_id in internal_online_users:
                    if internal_online_users[client_id]['socket'] != websocket:
                        await internal_online_users[client_id]['socket'].send_str(client_list_res_message)
                
                # Send updated internal client list to all online neighbour servers
                internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                for server_address in ONLINE_NEIGHBOURS:
                    # client_update_message = AssembleOutwardMessage("")
                    await ONLINE_NEIGHBOURS[server_address]['socket'].send(client_update_res_message)
            except Exception as e:
                raise(f"WS exception while closing: {e}")
                    
            break
    
    eventLogger("closeConnection", 1, disconnected_user, "")
    await websocket.close()
    
    return websocket

async def handle_upload_file(request):
    global SELF_ADDRESS
        
    try:
        data = await request.post()

        # added by Khanh - 13/10/2024

        # Checking file size
        uploaded_file = data.get("file")
        MAX_FILE_SIZE = 1024 * 1024 * 2
        uploaded_file.file.seek(0,2) # the second parameter "whence" means the position of the file pointer 
                                 # current position is relative to the end of the file
        file_size = uploaded_file.file.tell()
        if file_size > MAX_FILE_SIZE:
            response = {
                "body": {
                        "Error": "File size too large"
                }
            }
            return web.Response(text=json.dumps(response), content_type='application/json', status=413)
        
        # Checking file extensions
        allowed_types = ['txt','pdf','jpg', 'png']
        ext = uploaded_file.filename.lower().split('.')[-1]
        if ext not in allowed_types:
            response = {
            "body": {
                "Error": "Invalid file type"
                }
            }
            return web.Response(text=json.dumps(response), content_type="application/json", status=415)
        
        escaped_filename = re.sub(r"\s+","_",uploaded_file.filename)

        if uploaded_file == ("No data"):
            return web.Response(text="No Data")
        
        current_time = datetime.now()
        unix_timestamp = int(current_time.timestamp())
        escaped_filename += f"{unix_timestamp}"
        
        # Create a SHA-1 hash object
        sha256_hash = hashlib.sha256()
        
        # Update the hash object with the bytes of the string
        sha256_hash.update(escaped_filename.encode('utf-8'))
        
        # Get the hexadecimal representation of the hash
        hashed_filename = sha256_hash.hexdigest()
        
        with open(f"./upload/{hashed_filename}.{ext}", "wb") as fout:
            uploaded_file.file.seek(0,0) 
            fout.write(uploaded_file.file.read())

        response = {
            'body': {
                'file_url': f"http://{SELF_ADDRESS}/upload/{hashed_filename}.{ext}"
            }
        }

        return web.Response(text=json.dumps(response), content_type='application/json')
    except:
        return web.Response(status=403)

async def handle_download_file(request):
    
    filename = request.match_info['filename']
    file_path = os.path.join(os.getcwd(), f'./upload/{filename}')

    if not os.path.exists(file_path):
        return web.Response(text="File not found", status=404)

    return web.FileResponse(file_path)
    

# Start WS server
def main():
    
    app = web.Application()
    app.router.add_get('/', ws_handler)
    app.router.add_post('/api/upload', handle_upload_file)
    app.router.add_get('/upload/{filename:.*}', handle_download_file)
    
    # await init_server_connection()
    app.on_startup.append(server_startup)
    web.run_app(app, host="0.0.0.0", port=int(state['port']))

# Run the server
if __name__ == "__main__":
    # asyncio.run(main())
    main()
