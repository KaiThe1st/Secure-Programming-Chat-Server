import asyncio
import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json

online_users_on_servers = {
    
}

with open("./state.json", 'r') as server_state:
    state = json.load(server_state)
    
SELF_ADDRESS = f'{state["ip"]}:{state["port"]}'
NEIGHBOURS = state["neighbours"]

online_users_on_servers[SELF_ADDRESS] = {}

# WebSocket server handler
async def handler(websocket):
    
    # Send server_hello when the 
    # for idx in range(len(NEIGHBOURS)):
    #     server_websocket = await websockets.connect(NEIGHBOURS[idx]["address"])
    #     NEIGHBOURS[idx]["socket"] = server_websocket
    
    while True:
        try:
            
            client_id = "-1"
            message = await websocket.recv()
            print(1)
            # Identify the user who sent the message
            # By comaparing the sending websocket object against the recorded websocket object
            for server_address in online_users_on_servers:
                for id in online_users_on_servers[server_address]:
                    # print(online_users_on_servers[server_address][id]["socket"])
                    if online_users_on_servers[server_address][id]["socket"] == websocket: # or online_users_on_servers[server_address][id]["socket"] == websocket:
                        client_id = id
                        # print(id)
                        break
            
            # Process the Message
            # type: a message type as defined in the protocol document in the form f"{type}_{sub_type}"
            # status : 
            # sent_from: user_id
            # log_message: recording the event
            
            type, status, log_message, sent_from, parsed_message = ProcessInMessage(message, client_id)
            
            eventLogger(type, status, sent_from, log_message)
            
            
            # Store the websocket object if it is not yet recorded
            # if sent_from not in online_users and sent_from != "-1":
            #     online_users[sent_from] = websocket
            if type == "signed_data_hello":
                if sent_from not in online_users_on_servers[SELF_ADDRESS] and sent_from != -1:
                    online_users_on_servers[SELF_ADDRESS][sent_from] = {}
                    online_users_on_servers[SELF_ADDRESS][sent_from]["socket"] = websocket
                    online_users_on_servers[SELF_ADDRESS][sent_from]["public_key"] = parsed_message["data"]["public_key"]
                    
                
            
            # Send a acknowledgement message back to client
            if type == "client_list_request":
                
                # If the request is sent from a server, send the list of online users on this server
                # If the request is from a client, send client_list_request to neighbour servers
                
                
                all_online_users = ProcessOnlineUsersList(online_users_on_servers)
                
                return_message = AssembleOutwardMessage("client_list", all_online_users)
                
                await websocket.send(return_message)
            elif type == "signed_data_chat":
                return_message = AssembleOutwardMessage("signed_data_chat", all_online_users)
                await websocket.send(return_message)
                
            else:
                await websocket.send(f'ACK: {log_message}')

        except websockets.ConnectionClosedOK:
            disconnected_user = "unknown"
            for server_address in online_users_on_servers:
                for online_user in online_users_on_servers[server_address]:
                    if (online_users_on_servers[server_address][online_user] == websocket):
                        disconnected_user = online_user
                        del online_users_on_servers[server_address][online_user]
                        break
            eventLogger("closeConnection", 1, disconnected_user, "")
            break
        
        except websockets.ConnectionClosedError as e:
            disconnected_user = "unknown"
            for server_address in online_users_on_servers:
                for online_user in online_users_on_servers[server_address]:
                    if (online_users_on_servers[server_address][online_user] == websocket):
                        disconnected_user = online_user
                        del online_users_on_servers[server_address][online_user]
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
