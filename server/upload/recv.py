import asyncio
import websockets

async def websocket_client():
    uri = "ws://localhost:8080/"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to the WebSocket server")
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

# Running the WebSocket client
asyncio.run(websocket_client())