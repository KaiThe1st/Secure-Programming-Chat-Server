import asyncio
import websockets
from processMessage import ProcessInMessage
from processMessage import ProcessOnlineUsersList
from processMessage import AssembleOutwardMessage
from eventLogger import eventLogger
import json

online_users = {}

with open("./state.json", 'r') as server_state:
    state = json.load(server_state)

# WebSocket server handler
async def handler(websocket):
    while True:
        try:
            client_id = "-1"
            message = await websocket.recv()
            for id in online_users:
                if online_users[id] == websocket:
                    client_id = id
                    break
                
            type, status, log_message, sent_from = ProcessInMessage(message, client_id)
            
            eventLogger(type, status, sent_from, log_message)
            
            if sent_from not in online_users and sent_from != "-1":
                online_users[sent_from] = websocket
            # Send a acknowledgement message back to client
            if type == "client_list_request":
                all_online_users = ProcessOnlineUsersList(online_users, state, [])
                
                return_message = AssembleOutwardMessage("client_list", all_online_users)
                
                await websocket.send(return_message)
            elif type == "signed_data_chat":
                return_message = AssembleOutwardMessage("signed_data_chat", all_online_users)
                await websocket.send(return_message)
                
            else:
                await websocket.send(f'ACK: {log_message}')

        except websockets.ConnectionClosedOK:
            disconnected_user = "unknown"
            for user in online_users:
                if (online_users[user] == websocket):
                    disconnected_user = user
                    del online_users[user]
                    break
            eventLogger("closeConnection", 1, disconnected_user, "")
            break
        
        except websockets.ConnectionClosedError as e:
            disconnected_user = "unknown"
            for user in online_users:
                if (online_users[user] == websocket):
                    disconnected_user = user
                    del online_users[user]
                    break
            eventLogger("closeConnection", 1, disconnected_user, "Connection timeout")
            break



# Start WS server
async def main():
    async with websockets.serve(handler, state["ip"], state["port"], ping_interval=60, ping_timeout=120):
        eventLogger("serverGoOnline", 1, state["server_name"], f'at {state["ip"]}:{state["port"]}')
        # Keep the server alive 
        try:
            await asyncio.Future() 
        except asyncio.exceptions.CancelledError:
            eventLogger("serverGoOffline", 1, state["server_name"], "")

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
