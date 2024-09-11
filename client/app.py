import asyncio
import websockets

# Message handler
async def main():
    async with websockets.connect("ws://localhost:8080") as websocket:
        while True:
            try:
                message = input()
                await websocket.send(message)
                response = await websocket.recv()
                print(response)
            except websockets.ConnectionClosedOK:
                print('See you next time.')
                break

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
