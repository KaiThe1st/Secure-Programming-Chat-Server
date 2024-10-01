import asyncio
# import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json

from aiohttp import web, ClientConnectorError, WSServerHandshakeError
import aiohttp

internal_online_users = {
    
}

with open("./state.json", 'r') as server_state:
    state = json.load(server_state)
    
SELF_ADDRESS = f'{state["ip"]}:{state["port"]}'
NEIGHBOURS = state["neighbours"]
ONLINE_NEIGHBOURS = {}

# internal_online_users[SELF_ADDRESS] = {}
external_online_users = {}

async def init_server_connection():
    for idx in range(len(NEIGHBOURS)):
        
        if NEIGHBOURS[idx]["address"].strip() == SELF_ADDRESS:
            continue
        
        async with aiohttp.ClientSession() as session:
            try:
                distant_address = NEIGHBOURS[idx]["address"]
                server_websocket = await session.ws_connect(distant_address)
                ONLINE_NEIGHBOURS[distant_address]["socket"] = server_websocket
                ONLINE_NEIGHBOURS[distant_address]["counter"] = NEIGHBOURS[idx]["counter"]
                
                # Send 
                server_hello_mess = AssembleOutwardMessage("singed_data", "server_hello", SELF_ADDRESS)
                await server_websocket.send_bytes(server_hello_mess)
                
                client_update_request_mess = AssembleOutwardMessage("client_update_request", "", "")
                await server_websocket.send_bytes(client_update_request_mess)
                
            except ClientConnectorError as e:
            # Handle connection issues (e.g., server is down or unreachable)
                print(f"Connection error: {e}")
        
            except WSServerHandshakeError as e:
                print(f"WebSocket handshake failed: {e}")

            except asyncio.TimeoutError:
                print("Connection timed out.")

            except Exception as e:
                print(f"An error occurred: {e}")

# WebSocket server handler
async def handler(request):
    websocket = web.WebSocketResponse(heartbeat=30)
    await websocket.prepare(request) 
       
    
    async for msg in websocket:
        global internal_online_users
        
        from_user = "-1"
        from_server = 0
        if msg.type == aiohttp.WSMsgType.CLOSE:

            disconnected_user = "unknown"
            for online_user in internal_online_users:
                if (internal_online_users[online_user]["socket"] == websocket):
                    disconnected_user = online_user
                    del internal_online_users[online_user]
                    break
            eventLogger("closeConnection", 1, disconnected_user, "")
            await websocket.close()
            break
        
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
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip}:{distant_port}"
                for neigbour in NEIGHBOURS:
                    if neigbour["address"] == distant_address:
                        from_server == 1
                        break
                    
            
            # Process the Message
            # type: a message type as defined in the protocol document in the form f"{type}_{sub_type}"
            # status : 
            # sent_from: user_id
            # log_message: recording the event
            
            type, status, log_message, sent_from, parsed_message = ProcessInMessage(message, from_user, from_server)
            
            if type == None:
                continue
            
            
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
                    
                    # Send updated client list to all clients apart from the sender
                    for client_id in internal_online_users:
                        if internal_online_users[client_id]["socket"] != websocket:
                            await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                    
                    # Send updated internal client list to all online neighbour servers
                    internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                    client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                    for server_address in ONLINE_NEIGHBOURS:
                        # client_update_message = AssembleOutwardMessage("")
                        await ONLINE_NEIGHBOURS[server_address]["socket"].send_bytes(client_update_res_message)
                    
                    
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
                return_message = AssembleOutwardMessage("client_list", "", all_online_users)
                await websocket.send_bytes(return_message)
            
            # HANDLE REQUEST FOR CLIENT UPDATE FROM SERVERS
            elif type == "client_update_request" and from_server == 1:
                internal_clients = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_mess = AssembleOutwardMessage("client_update", "", internal_clients)
                await websocket.send_bytes(client_update_res_mess)
            
            # HANDLE CLIENT UPDATE
            elif type == "client_update" and from_server == 1:
                # for server_address in ONLINE_NEIGHBOURS:
                #     if ONLINE_NEIGHBOURS[server_address]["socket"] == websocket:
                #         external_online_users[server_address] = parsed_message["clients"]
                distant_ip, distant_port = request.transport.get_extra_info('peername')
                distant_address = f"{distant_ip.strip()}:{distant_port.strip()}"
                external_online_users[distant_address] = parsed_message["clients"]
                
                
                # Generate message to send to clients
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)    
                
                # Send the updated client list to all online clients connected to this server
                for client_id in internal_online_users:
                    if internal_online_users[client_id]["socket"] != websocket:
                        await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                
            # HANDLE CHAT
            elif type == "signed_data_chat" and sent_from != "-1":
                    
                # Send the message to all online neighbour servers
                if from_server == 0:
                    for neighbour in ONLINE_NEIGHBOURS:
                        try:
                            chat_msg = AssembleOutwardMessage("signed_data", "chat", parsed_message)
                            await ONLINE_NEIGHBOURS[neighbour]["socket"].send_bytes(chat_msg)
                        except Exception as e:
                            print(e)

                # Send the message to all online clients
                for client_id in internal_online_users:
                    chat_msg = AssembleOutwardMessage("signed_data", "chat", parsed_message)
                    socket = internal_online_users[client_id]["socket"]
                    # if socket != websocket:
                    await socket.send_bytes(chat_msg) 
                    print("Hello")
                    
                # await websocket.send_bytes(message)
                        
            # HANDLE PUBLIC CHAT
            elif type == "signed_data_public_chat" and sent_from != "-1":
                # Send message to neighbour servers when the message is from a client    
                if from_server == 0:
                    for neighbour in ONLINE_NEIGHBOURS:
                        try:
                            pub_chat_msg = AssembleOutwardMessage("signed_data", "chat", parsed_message)
                            await ONLINE_NEIGHBOURS[neighbour]["socket"].send_bytes(pub_chat_msg)
                        except Exception as e:
                            print(e)
                
                # Send the message to all online clients connected to this master server
                for client_id in internal_online_users:
                    pub_chat_msg = AssembleOutwardMessage("signed_data", "chat", parsed_message)
                    socket = internal_online_users[client_id]["socket"]
                    # if socket != websocket:
                    await socket.send_bytes(pub_chat_msg) 
                        
                        # print("Hello")
            
            else:
                await websocket.send_str(f'ACK: {log_message}')
            
            # await websocket.send_str(f'ACK: {log_message}')

        except Exception as e:
            print("=======")
            print(e)
            print("=======")
            
            
            
    # print("WebSocket connection closed")
    # When one client is closing the connection
    disconnected_user = "unknown"
    for online_user_id in internal_online_users:
        print()
        print(f"All online user: {internal_online_users}")
        print()
        print(f"Cur: {online_user_id}")
        print()
        if (internal_online_users[online_user_id]["socket"] == websocket):
            disconnected_user = online_user_id
            try:
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                client_list_res_message = AssembleOutwardMessage("client_list", "", all_online_users)
                
                # Send updated client list to all clients apart from the sender
                for client_id in internal_online_users:
                    if internal_online_users[client_id]["socket"] != websocket:
                        await internal_online_users[client_id]["socket"].send_bytes(client_list_res_message)
                
                # Send updated internal client list to all online neighbour servers
                internal_online_users_for_sending = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                client_update_res_message = AssembleOutwardMessage("client_update", "", internal_online_users_for_sending)
                for server_address in ONLINE_NEIGHBOURS:
                    # client_update_message = AssembleOutwardMessage("")
                    await ONLINE_NEIGHBOURS[server_address]["socket"].send_bytes(client_update_res_message)
            except Exception as e:
                raise(f"WS exception while closing: {e}")
                    
            del internal_online_users[online_user_id]
            break
    
    eventLogger("closeConnection", 1, disconnected_user, "")
    await websocket.close()
    
    return websocket

async def handle_upload_file(request):
    # filename = request.match_info['filename']
    # segments = filename.split('/')
    # if len(segments) != 1:
    #     return web.Response(text="Wrong format. Try again")
    
    data = await request.post()

    
    uploaded_file = data.get("file")
    
    if uploaded_file == ("No data"):
        return web.Response(text="No Data")
    
    with open(f"./upload/{uploaded_file.filename}", "wb") as fout:
        fout.write(uploaded_file.file.read())

    return web.Response(text="file received")

async def handle_download_file(request):
    pass


# Start WS server
def main():
    
    app = web.Application()
    app.router.add_get('/', handler)
    app.router.add_post('/api/upload', handle_upload_file)
    app.router.add_get('/upload/{filename:.*}', handle_download_file)
    
    web.run_app(app, host=state["host_ip"], port=int(state["port"]))    

# Run the server
if __name__ == "__main__":
    main()