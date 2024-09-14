import asyncio
import websockets
import json

from parseMessage import ParseOutMessage
from parseMessage import ParseInMessage


# Message handler
async def main():
    
    # Load server information in
    ip = "127.0.0.1"
    port = 8080
    with open("./server_info.json", 'r') as server_info:
        data = json.load(server_info)
        ip = data["master_server_ip"]
        port = data["master_server_port"]
        
    async with websockets.connect(f"ws://{ip}:{port}") as websocket:
        print('-------------------')
        print('Connecting to')
        print(f"ws://{ip}:{port}")
        print('-------------------')
        
        # Connection request to a server
        helloMessage = ParseOutMessage("", "signed_data", "hello")
        await websocket.send(helloMessage)
        response = await websocket.recv()
        print(response)
        
        
        # Request the list of online clients from all approachable servers
        requestClientList = ParseOutMessage("", "client_list_request", "")
        await websocket.send(requestClientList)
        response = await websocket.recv()
        response = ParseInMessage(response)
        print(response)
        
        
        while True:
            try:
                message = input()
                parsedMessage = ParseOutMessage(message, "signed_data", "chat")
                await websocket.send(parsedMessage)
                response = await websocket.recv()
                print(response)
            except websockets.ConnectionClosedOK:
                print('See you next time.')
                break
            except websockets.ConnectionClosedError as e:
                print(f"Close Error: {e}")
                await asyncio.sleep(5)

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
