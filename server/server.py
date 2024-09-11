import asyncio
import websockets

# WebSocket server handler
async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(message)
            await websocket.send(f'ACK: {message}')

        except websockets.ConnectionClosedOK:
            print('connection closed from 1 client')
            break


# Start WS server
async def main():
    async with websockets.serve(handler, "localhost", 8080):
        print("WebSocket server is running on ws://localhost:8080")
        # Keep the server alive 
        await asyncio.Future() 

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
