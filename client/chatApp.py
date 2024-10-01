from parseMessage import ParseOutMessage
from parseMessage import ParseInMessage
from rsaKeyGenerator import generate_key_pair
import asyncio
import hashlib
import os
import websockets
import json
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton
from PyQt5 import QtCore
import logging

# logging.basicConfig(level=logging.DEBUG)

ONLINE_USERS = []


class G40chatApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group40chatApp")
        self.setGeometry(100, 100, 800, 600)  # Set an initial size, but it'll adjust based on screen size
        
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Side menu (on the left)
        self.side_menu = QTextEdit(self)
        self.side_menu.setReadOnly(True)
        
        # Title above the side menu (labeled "Chats")
        self.side_menu_title = QLabel("Chats", self)
        self.side_menu_title.setStyleSheet("font-weight: bold; font-size: 16px;")  # Style for the label
        
        # Add buttons for "Public Chat" and "Private Chat"
        self.public_chat_button = QPushButton("Public Chat", self)
        self.private_chat_button = QPushButton("New Private Chat", self)
        
        # Placeholder for chat type switch functionality
        # self.public_chat_button.clicked.connect(self.switch_to_public_chat)
        # self.private_chat_button.clicked.connect(self.switch_to_private_chat)

        # Chat display (in the center)
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)

        self.chat_display_title = QLabel("Name of User", self)  # Chat title (can change based on chat context)
        self.chat_display_title.setStyleSheet("font-weight: bold; font-size: 16px;")  # Style for the label  

        # Message input (bottom)
        self.message_input = QLineEdit(self)
        self.message_input.returnPressed.connect(self.send_message)

        # Upload button (left of the message input)
        self.upload_button = QPushButton("Upload File", self)
        # self.upload_button.clicked.connect(self.upload_image)

        # Send button (right of the message input)
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        # Side menu layout (fixed width)
        side_layout = QVBoxLayout()
        side_layout.addWidget(self.side_menu_title)  # Add the title above the side menu
        side_layout.addWidget(self.public_chat_button)  # Add Public Chat button
        side_layout.addWidget(self.private_chat_button)  # Add Private Chat button
        side_layout.addWidget(self.side_menu)  # Add the chat list itself
        side_layout.setStretch(3, 1)  # Make the side menu take as much space as possible
        main_layout.addLayout(side_layout)

        # Chat layout (center and bottom area)
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_display_title)  # Add the title above the chat display
        chat_layout.addWidget(self.chat_display)
        
        # Input layout (message input, upload button, send button)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.upload_button)   # Add the upload button here
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        main_layout.addLayout(chat_layout)

        # Stretch factors for dynamic resizing
        main_layout.setStretch(0, 1)  # Side menu takes 1/5 of space
        main_layout.setStretch(1, 4)  # Chat display and input take 4/5 of space

        # WebSocket thread for handling chat connections
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
                helloMessage = ParseOutMessage("", "signed_data", "hello", [], ONLINE_USERS)
                await self.websocket.send(helloMessage)
                response = await self.websocket.recv()
                print(response)

                # Request online clients in approachable servers
                requestClientList = ParseOutMessage("", "client_list_request", "", [], ONLINE_USERS)
                await self.websocket.send(requestClientList)
                response = await self.websocket.recv()
                response = ParseInMessage(response)
                print(response)
                
                # Continuously waiting for message from server
                while True:
                    try:
                        message = await websocket.recv()
                        msg = ParseInMessage(message)  
                        self.message_received.emit(f"Received: {msg}") 
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
        parsedMessage = ParseOutMessage(message, "signed_data", "public_chat", [], ONLINE_USERS)
        asyncio.run_coroutine_threadsafe(self.websocket_send(parsedMessage), self.loop)
    
    # 
    # 
    def send_public_message(self, message):
        parsedMessage = ParseOutMessage(message, "signed_data", "public_chat", [], ONLINE_USERS)
        asyncio.run_coroutine_threadsafe(self.websocket_send(parsedMessage), self.loop)

    # Actual function that send the message
    async def websocket_send(self, message):
        if self.connected and self.websocket:
            await self.websocket.send(message) 

if (not(os.path.isfile("private_key.pem") and os.path.isfile("public_key.pem"))):
    generate_key_pair()

if (not(os.path.isfile("client_state.json"))):
    with open("client_state.example.json", "r") as file:
        client_state = json.load(file)
    with open("client_state.json", "w") as file:
        json.dump(client_state, file, indent=4)

with open("client_state.json", "r") as file:
    client_state = json.load(file)
    if (client_state["fingerprint"] == ""):
        with open("public_key.pem", "r") as pub_f:
            pub_k = pub_f.read()
            client_state["fingerprint"] = hashlib.sha256(pub_k.encode()).hexdigest()

with open("client_state.json", "w") as file:
    json.dump(client_state, file, indent=4)

app = QtWidgets.QApplication(sys.argv)
window = G40chatApp()
window.showMaximized()

window.websocket_thread.message_received.connect(window.display_message)

sys.exit(app.exec_())