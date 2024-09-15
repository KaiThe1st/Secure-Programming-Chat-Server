from parseMessage import ParseOutMessage
from parseMessage import ParseInMessage
import asyncio
import websockets
import json
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout



class G40chatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group40chatApp")
        self.setGeometry(0, 0, 1900, 1080)

        
        self.side_menu = QtWidgets.QTextEdit(self)
        self.side_menu.setGeometry(0, 0, 380, 1820)
        self.side_menu.setReadOnly(True)
        
        
        self.chat_display = QtWidgets.QTextEdit(self)
        self.chat_display.setGeometry(380, 0, 1540, 900)
        self.chat_display.setReadOnly(True)
        
        
        self.message_input = QtWidgets.QLineEdit(self)
        self.message_input.setGeometry(380, 905, 1420, 80)

        self.send_button = QtWidgets.QPushButton("Send", self)
        self.send_button.setGeometry(1800, 905, 120, 80)
        self.send_button.clicked.connect(self.send_message)
        
        

        self.websocket_thread = WebsocketConnection(self)
        self.websocket_thread.start()

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.websocket_thread.send_message(message)
            self.message_input.clear()

    def display_message(self, message):
        self.chat_display.append(message)

# Thread for handling login behind
class WebsocketConnection(QtCore.QThread):
    message_received = QtCore.pyqtSignal(str)  

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected = False
        self.websocket = None
        self.loop = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_connect())


    async def websocket_connect(self):
        ip = "127.0.0.1"
        port = 8080
        with open("./server_info.json", 'r') as server_info:
            data = json.load(server_info)
        ip = data["master_server_ip"]
        port = data["master_server_port"]
        WS_SERVER = f"ws://{ip}:{port}"
        try:
            async with websockets.connect(WS_SERVER) as websocket:                
                self.websocket = websocket
                self.connected = True
                print('-------------------')
                print('Connecting to')
                print(f"ws://{ip}:{port}")
                print('-------------------')

                # Connection request to a server
                helloMessage = ParseOutMessage("", "signed_data", "hello")
                await self.websocket.send(helloMessage)
                response = await self.websocket.recv()
                print(response)

                # Request online clients in approachable servers
                requestClientList = ParseOutMessage("", "client_list_request", "")
                await self.websocket.send(requestClientList)
                response = await self.websocket.recv()
                response = ParseInMessage(response)
                print(response)

                while True:
                    try:
                        message = await websocket.recv()  
                        self.message_received.emit(f"Received: {message}") 
                    except websockets.ConnectionClosedOK:
                        print('See you next time.')
                        break
                    except websockets.ConnectionClosedError as e:
                        print(f"Close Error: {e}")
                        break         
        
        except Exception as e:
            print(f"WebSocket connection error: {e}")

    # A handler when the UI receive a send request
    # Assign the send functionality to another thread
    def send_message(self, message):
        parsedMessage = ParseOutMessage(message, "signed_data", "chat")
        asyncio.run_coroutine_threadsafe(self.websocket_send(parsedMessage), self.loop)

    # Actual function that send the message
    async def websocket_send(self, message):
        if self.connected and self.websocket:
            await self.websocket.send(message) 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = G40chatApp()
    window.showMaximized()

    window.websocket_thread.message_received.connect(window.display_message)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
