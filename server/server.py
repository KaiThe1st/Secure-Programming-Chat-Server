import asyncio
import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json
import os
import logging
import socket
from rsaKeyGenerator import generate_key_pair

logging.basicConfig(level=logging.DEBUG)

from aiohttp import web, ClientConnectorError, WSServerHandshakeError
import aiohttp

internal_online_users = {
    
}

IP = socket.gethostbyname(socket.gethostname())

if (not(os.path.isfile("private_key.pem") and os.path.isfile("public_key.pem"))):
    generate_key_pair()
    
if (not(os.path.isfile("state.json"))):
    with open('state.example.json', 'r') as f:
        server_state = json.load(f)
        server_state["neighbours"] = []
    with open('state.json', 'w') as f:
        json.dump(server_state, f, indent=4)


with open("./state.json", 'r') as server_state:
    state = json.load(server_state)
    state["ip"] = IP
    
print(f'I am : {IP}')

SELF_ADDRESS = f'{state["ip"]}:{state["port"]}'
NEIGHBOURS = state["neighbours"]
ONLINE_NEIGHBOURS = {}
ONLINE_NEIGHBOURS_SENT = []

# internal_online_users[SELF_ADDRESS] = {}
external_online_users = {}

async def server_startup(app):
    for idx in range(len(NEIGHBOURS)):
        
        if NEIGHBOURS[idx]["address"].strip() == SELF_ADDRESS or NEIGHBOURS[idx]["address"].strip() in ONLINE_NEIGHBOURS_SENT: # or NEIGHBOURS[idx]["address"].strip() in ONLINE_NEIGHBOURS:
            continue
        
        ONLINE_NEIGHBOURS_SENT.append(NEIGHBOURS[idx]["address"].strip())
        distant_address = "ws://" + NEIGHBOURS[idx]["address"] + "/"
        
        asyncio.create_task(init_server_connection(distant_address, idx))
        # await init_server_connection(distant_address, idx)
        
# async def keep_alive():
#     while True:
#         await asyncio.sleep(10)
#         continue
        

async def init_server_connection(distant_address, idx):
    print(NEIGHBOURS)
    async with websockets.connect(distant_address, ping_interval=10) as server_websocket:
        try:
            # Send 
            server_hello_mess = AssembleOutwardMessage("signed_data", "server_hello", SELF_ADDRESS)
            print(server_hello_mess)
            await server_websocket.send(server_hello_mess)
            
            client_update_request_mess = AssembleOutwardMessage("client_update_request", "", "")
            print(client_update_request_mess)
            await server_websocket.send(client_update_request_mess)
            print("here")
            # server_websocket = await session.ws_connect(distant_address)
            if distant_address not in ONLINE_NEIGHBOURS:
                ONLINE_NEIGHBOURS[distant_address] = {}
            ONLINE_NEIGHBOURS[distant_address]["socket"] = server_websocket
            ONLINE_NEIGHBOURS[distant_address]["counter"] = NEIGHBOURS[idx]["counter"]
            print("ha")
            # asyncio.create_task(keep_alive)
            
            while True:
                # await websockets.recv()
                await asyncio.sleep(10)
                # print("hi")
                continue
        # except ClientConnectorError as e:
        # # Handle connection issues (e.g., server is down or unreachable)
        #     print(f"Connection error: {e}")
    
        # except WSServerHandshakeError as e:
        #     print(f"WebSocket handshake failed: {e}")
        # except asyncio.TimeoutError:
        #     print("Connection timed out.")
        except Exception as e:
            print(f"An error occurred: {e}")
    # aync with websockets.connect("ws://10.13.91.49:8080/") as websocket:
    #     try:
    #         await websocket.send("Hello Server")
    #     except Exception as e:
    #         print(f"THe fking error is: {e}")
            


# WebSocket server handler
async def ws_handler(request):
    websocket = web.WebSocketResponse(heartbeat=30)
    await websocket.prepare(request) 
    
    # await init_server_connection()
       
    
    async for msg in websocket:
        global internal_online_users
        
        print("_____________________---")
        print(msg)
        
        from_user = "-1"
        from_server = 0
        # if msg.type == aiohttp.WSMsgType.CLOSE:

        #     disconnected_user = "unknown"
        #     for online_user in internal_online_users:
        #         if (internal_online_users[online_user]["socket"] == websocket):
        #             disconnected_user = online_user
        #             del internal_online_users[online_user]
        #             break
        #     # eventLogger("closeConnection", 1, disconnected_user, "")
        #     await websocket.close()
        #     break
        
        try:

            message = msg.data

            # Identify the user who sent the message
            # By comaparing the sending websocket object against the recorded websocket object
            # for server_address in internal_online_users:
            for id in internal_online_users:
                # print(internal_online_users[server_address][id]["socket"])
                if internal_online_users[id]["socket"] == websocket:
                    from_user = id
                    # print(id)
                    break



            if from_user == "-1":
                # if request is not None:
                    
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip.strip()}"
                print(distant_address)
                for neigbour in NEIGHBOURS:
                    if neigbour["address"].split(":")[0] == distant_address:
                        from_server = 1
                        break
   
            
            # Process the Message
            # type: a message type as defined in the protocol document in the form f"{type}_{sub_type}"
            # status : 
            # sent_from: user_id
            # log_message: recording the event
            
            type, status, log_message, sent_from, parsed_message = ProcessInMessage(message, from_user, from_server)
            
            if type == None:
                continue
            
            
            print("++++++++++++++++++++++")
            print(from_server)
            print(from_user)
            print(message)
            print("++++++++++++++++++++++")
            
            if sent_from != "-1" or from_server == 1:
                # await websocket.close(code=4000, reason="Limited one client on a host")
            
                eventLogger(type, status, sent_from, log_message)
            
            # HANDLE HELLO
            if type == "signed_data_hello" and from_server == 0 and sent_from != "-1":
                # prevent multiconnection on a single client
                if sent_from in internal_online_users \
                    and internal_online_users[sent_from]["socket"] is not websocket:
                        # await web.Response(text="Access denied.", status=403)
                        continue
                
                if sent_from not in internal_online_users:
                    internal_online_users[sent_from] = {}
                    internal_online_users[sent_from]["socket"] = websocket
                    internal_online_users[sent_from]["public_key"] = parsed_message["data"]["public_key"]
                    
                    # Process an updated list of users
                    all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                    client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)
                    
                    # Send updated client list to all other clients apart from the sender
                    for client_id in internal_online_users:
                        if internal_online_users[client_id]["socket"] != websocket:
                            await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                    
                    # Send updated internal client list to all online neighbour servers
                    internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                    client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                    for server_address in ONLINE_NEIGHBOURS:
                        # client_update_message = AssembleOutwardMessage("")
                        await ONLINE_NEIGHBOURS[server_address]["socket"].send(client_update_res_message)
                    
                    
                    await websocket.send_str("Connection established")

            # HANDLE SERVER HELLO
            elif type == "signed_data_server_hello" and from_server == 1:
                sending_server = parsed_message["data"]["sender"]
                # if sending_server not in ONLINE_NEIGHBOURS:
                #     ONLINE_NEIGHBOURS.append(sending_server)
                ONLINE_NEIGHBOURS[sending_server]["socket"] = websocket
                # return_message = AssembleOutwardMessage("signed_data", "server_hello", SELF_ADDRESS)
                
                # await websocket.send_bytes(return_message)
                
            # HANDLE REQUEST FOR ONLINE CLIENTS
            elif type == "client_list_request" and from_server == 0 and sent_from != "-1":
                
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_mess = AssembleOutwardMessage("client_list", "", all_online_users)
                await websocket.send_bytes(client_list_res_mess)
            
            # HANDLE REQUEST FOR CLIENT UPDATE FROM SERVERS
            elif type == "client_update_request" and from_server == 1:
                internal_clients = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_mess = AssembleOutwardMessage("client_update", "", internal_clients)
                await websocket.send_bytes(client_update_res_mess)
                
            
            # HANDLE CLIENT UPDATE
            elif type == "client_update": # and from_server == 1:
                # for server_address in ONLINE_NEIGHBOURS:
                #     if ONLINE_NEIGHBOURS[server_address]["socket"] == websocket:
                #         external_online_users[server_address] = parsed_message["clients"]
                
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip.strip()}:{distant_port}"
                external_online_users[distant_address] = parsed_message["clients"]
                
                print("YYYYYYYYYYYYYYYYYYYYYYYY")
                print(parsed_message)
                print("YYYYYYYYYYYYYYYYYYYYYYYY")
            
            
                # Generate message to send to clients
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)    
                # Send the updated client list to all online clients connected to this server
                
                print(client_list_res_message)
                
                for client_id in internal_online_users:
                    if internal_online_users[client_id]["socket"] != websocket:
                        await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                
            # HANDLE CHAT
            elif type == "signed_data_chat": # and sent_from != "-1":
                    
                # Send the message to all online neighbour servers
                if from_server == 0:
                    # prev = ""
                    for neighbour in ONLINE_NEIGHBOURS:
                        # print(neigbour)
                        # if neighbour in parsed_message["data"]["destination_servers"] and prev != neigbour:
                        try:
                            await ONLINE_NEIGHBOURS[neighbour]["socket"].send(message)
                            # prev = neighbour
                        except Exception as e:
                            print(e)

                # Send the message to all online clients
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    if socket != websocket:
                        await socket.send_bytes(message) 
                    
                        
            # HANDLE PUBLIC CHAT
            elif type == "signed_data_public_chat": # and sent_from != "-1":
                # Send message to neighbour servers when the message is from a client    
                if from_server == 0:
                    for neighbour in ONLINE_NEIGHBOURS:
                        try:
                            await ONLINE_NEIGHBOURS[neighbour]["socket"].send(message)
                        except Exception as e:
                            print(e)
                
                # Send the message to all online clients connected to this master server
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    if socket != websocket:
                        await socket.send_bytes(message) 
                        
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
        if (internal_online_users[online_user_id]["socket"] == websocket):
            disconnected_user = online_user_id
            
            del internal_online_users[online_user_id]
            
            try:
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)
                print(client_list_res_message)
                
                # Send updated client list to all clients apart from the sender
                for client_id in internal_online_users:
                    if internal_online_users[client_id]["socket"] != websocket:
                        await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                
                # Send updated internal client list to all online neighbour servers
                internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                for server_address in ONLINE_NEIGHBOURS:
                    # client_update_message = AssembleOutwardMessage("")
                    await ONLINE_NEIGHBOURS[server_address]["socket"].send(client_update_res_message)
            except Exception as e:
                raise(f"WS exception while closing: {e}")
                    
            break
    
    eventLogger("closeConnection", 1, disconnected_user, "")
    await websocket.close()
    
    return websocket

async def handle_upload_file(request):
    # filename = request.match_info['filename']
    # segments = filename.split('/')
    # if len(segments) != 1:
    #     return web.Response(text="Wrong format. Try again")
    global SELF_ADDRESS
    try:
        data = await request.post()


        uploaded_file = data.get("file")

        if uploaded_file == ("No data"):
            return web.Response(text="No Data")

        with open(f"./upload/{uploaded_file.filename}", "wb") as fout:
            fout.write(uploaded_file.file.read())

        response = {
            'body': {
                'file_url': f"http://{SELF_ADDRESS}/upload/{uploaded_file.filename}"
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
    web.run_app(app, host="0.0.0.0", port=int(state["port"]))

# Run the server
if __name__ == "__main__":
    # asyncio.run(main())
    main()