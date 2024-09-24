import asyncio
import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json

internal_online_users = {
    
}

with open("./state.json", 'r') as server_state:
    state = json.load(server_state)
    
SELF_ADDRESS = f'{state["ip"]}:{state["port"]}'
NEIGHBOURS = state["neighbours"]
ONLINE_NEIGHBOURS = {}

# internal_online_users[SELF_ADDRESS] = {}
external_online_users = {}

# WebSocket server handler
async def handler(websocket):
    
    # Send server_hello when the 
    for idx in range(len(NEIGHBOURS)):
        if NEIGHBOURS[idx]["address"].strip() == SELF_ADDRESS:
            continue
        server_websocket = await websockets.connect(NEIGHBOURS[idx]["address"])
        NEIGHBOURS[idx]["socket"] = server_websocket
        
        # try:
        #     async with websockets.connect(f'ws://{dest}') as to_server_websocket:
        #         await to_server_websocket.send(message)
        #         print("hello")
        # except:
        #     pass
            
    
    while True:
        from_id = "-1"
        try:
            global internal_online_users

            message = await websocket.recv()
            # Identify the user who sent the message
            # By comaparing the sending websocket object against the recorded websocket object
            # for server_address in internal_online_users:
            for id in internal_online_users:
                # print(internal_online_users[server_address][id]["socket"])
                if internal_online_users[id]["socket"] == websocket:
                    from_id = id
                    # print(id)
                    break
            
            if from_id == "-1":    
                distant_connector = websocket.remote_address
                distant_address = f"{distant_connector[0]}:{distant_connector[1]}"
                for neigbour in NEIGHBOURS:
                    if neigbour["address"] == distant_address:
                        from_id == distant_address
            
            # Process the Message
            # type: a message type as defined in the protocol document in the form f"{type}_{sub_type}"
            # status : 
            # sent_from: user_id
            # log_message: recording the event
            
            type, status, log_message, sent_from, parsed_message = ProcessInMessage(message, from_id)
            
            if type == None:
                continue
            
            
            if sent_from != "-1":
                # await websocket.close(code=4000, reason="Limited one client on a host")
            
                eventLogger(type, status, sent_from, log_message)
            
            
            # Store the websocket object if it is not yet recorded
            # if sent_from not in online_users and sent_from != "-1":
            #     online_users[sent_from] = websocket
            
            # HANDLE HELLO
            if type == "signed_data_hello":
                if sent_from in internal_online_users \
                    and internal_online_users[sent_from]["socket"] is not websocket:
                        await websocket.close(code=4000, reason="Limited one client on a host")
                        continue
                
                if sent_from not in internal_online_users and sent_from != -1:
                    # print(websocket)
                    internal_online_users[sent_from] = {}
                    internal_online_users[sent_from]["socket"] = websocket
                    internal_online_users[sent_from]["public_key"] = parsed_message["data"]["public_key"]
                    
                    for client_id in internal_online_users:
                        if internal_online_users[client_id]["socket"] != websocket:
                            
                            all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, [])
                            return_message = AssembleOutwardMessage("client_list", "", all_online_users)
                            await internal_online_users[client_id]["socket"].send(return_message)
                    
                    await websocket.send("Connection established")

            # HANDLE SERVER HELLO
            elif type == "signed_data_server_hello":
                sending_server = parsed_message["data"]["sender"]
                # if sending_server not in ONLINE_NEIGHBOURS:
                #     ONLINE_NEIGHBOURS.append(sending_server)
                ONLINE_NEIGHBOURS[sending_server] = websocket
                return_message = AssembleOutwardMessage("signed_data", "server_hello", SELF_ADDRESS)
                
                await websocket.send(return_message)
                
            # HANDLE REQUEST FOR ONLINE CLIENTS
            elif type == "client_list_request":
                
                client_update_request = AssembleOutwardMessage("client_update_request", "", "")
                external_clients = []
                
                # for server_address in ONLINE_NEIGHBOURS:
                #     try:
                #         async with websockets.connect(f'ws://{dest}') as to_server_websocket:
                #             await to_server_websocket.send(client_update_request)
                #             client_update_response = await to_server_websocket.recv()
                #             type, status, log_message, sent_from, parsed_client_list = ProcessInMessage(client_update_response, "external_server")
                #             external_clients.append(parsed_client_list["servers"])
                            
                        
                #     except:
                #         pass
                
                
                all_online_users = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, external_online_users)
                
                
                return_message = AssembleOutwardMessage("client_list", "", all_online_users)
                await websocket.send(return_message)
            
            # HANDLE REQUEST FOR CLIENT UPDATE FROM SERVERS
            elif type == "client_update_request":
                internal_clients = ProcessOnlineUsersList(internal_online_users, SELF_ADDRESS, {})
                return_message = AssembleOutwardMessage("client_update", "", internal_clients)
                await websocket.send(return_message)
            
            # HANDLE CLIENT UPDATE
            elif type == "client_update":
                for server_address in ONLINE_NEIGHBOURS:
                    if ONLINE_NEIGHBOURS[server_address] == websocket:
                        external_online_users[server_address] = parsed_message["clients"]
                
                pass
                
            # HANDLE CHAT
            elif type == "signed_data_chat":
                # Identify if a message is from a client or a server
                isFromServer = True
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    # When the signed_data_chat is sent from a online client of this server
                    if socket == websocket:
                        isFromServer == False
                        
                        # print(parsed_message["data"]["destination_servers"])
                        destinations = parsed_message["data"]["destination_servers"]
                        prev = ""
                        for dest in destinations:
                            if dest == prev:
                                continue
                            try:
                                
                                async with websockets.connect(f'ws://{dest}') as to_server_websocket:
                                    await to_server_websocket.send(message)
                                    print("hello")
                            except:
                                pass
                            prev = dest
                        
                        break

                # if isFromServer == True:
                #     continue
                
                # In case the message is sent from a server
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    if socket != websocket:
                        await socket.send(message) 
                        
            # HANDLE PUBLIC CHAT
            elif type == "signed_data_public_chat":
                # Identify if a message is from a client or a server
                isFromServer = True
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    # Send message to neighbour servers when the message is from a client
                    if socket == websocket:
                        isFromServer == False
                        
                        # print(parsed_message["data"]["destination_servers"])
                        prev = ""
                        for dest in ONLINE_NEIGHBOURS:
                            if dest == prev:
                                continue
                            try:
                                async with websockets.connect(f'ws://{dest}') as to_server_websocket:
                                    await to_server_websocket.send(message)
                                    print("hello")
                            except:
                                pass
                            prev = dest
                        
                        break
                
                # Send the message to all online clients connected to this master server
                for client_id in internal_online_users:
                    socket = internal_online_users[client_id]["socket"]
                    if socket != websocket:
                        await socket.send(message) 
            
            else:
                await websocket.send(f'ACK: {log_message}')

        except websockets.ConnectionClosedOK:
            disconnected_user = "unknown"
            for online_user in internal_online_users:
                if (internal_online_users[online_user]["socket"] == websocket):
                    disconnected_user = online_user
                    del internal_online_users[online_user]
                    break
            eventLogger("closeConnection", 1, disconnected_user, "")
            break
        
        except websockets.ConnectionClosedError as e:
            disconnected_user = "unknown"
            for online_user in internal_online_users:
                if (internal_online_users[online_user]["socket"] == websocket):
                    disconnected_user = online_user
                    del internal_online_users[online_user]
                    break
            eventLogger("closeConnection", 1, disconnected_user, "Connection timeout")
            break


# Start WS server
async def main():
    async with websockets.serve(handler, state["host_ip"], state["port"], ping_interval=60, ping_timeout=120):
        eventLogger("serverGoOnline", 1, state["server_name"], f'at {state["ip"]}:{state["port"]}')
        # Keep the server alive 
        try:
            await asyncio.Future() 
        except asyncio.exceptions.CancelledError:
            eventLogger("serverGoOffline", 1, state["server_name"], "")

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
