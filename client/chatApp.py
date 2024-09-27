from parseMessage import ParseOutMessage
from parseMessage import ParseInMessage
import asyncio
import websockets
import json
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton, QListWidget
from PyQt5 import QtCore
import logging

# logging.basicConfig(level=logging.DEBUG)
ONLINE_USERS = []
class PrivateChatDialog(QtWidgets.QDialog):
    def __init__(self, online_users, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start Private Chat")
        self.setGeometry(300, 200, 400, 300)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Select users to chat with:", self)
        layout.addWidget(self.label)
        
        # List of online users with multi-selection mode
        self.user_list = QtWidgets.QListWidget(self)

        print()
        print()
        print(ONLINE_USERS)
        print()
        print()

        # Check if online_users is structured as expected
        for entry in ONLINE_USERS:
            clients = entry['clients']

        print(clients)
        # Add each client to the user_list
        for user in clients:
            self.user_list.addItem(user)

        self.user_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)  # Allow multiple selections
        layout.addWidget(self.user_list)
        
        # Create button to start private chat
        self.create_button = QPushButton("Create", self)
        self.create_button.clicked.connect(self.create_chat)
        layout.addWidget(self.create_button)

    def create_chat(self):
        selected_items = self.user_list.selectedItems()
        if selected_items:
            users = [item.text() for item in selected_items]  # Get a list of selected users
            print(f"Starting private chat with: {', '.join(users)}")
            self.accept()  # Close the dialog
            self.result = users  # Return the list of selected users


class G40chatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group40chatApp")
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Side menu (on the left)
        self.side_menu = QListWidget(self)
        self.side_menu.setSelectionMode(QListWidget.SingleSelection)
        
        self.side_menu_title = QLabel("Chats", self)
        self.side_menu_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        # Add "Public Chat" at the start
        self.side_menu.addItem("Public Chat")
        self.side_menu.itemClicked.connect(self.change_chat)

        # Button to initiate new private chat
        self.private_chat_button = QPushButton("New Private Chat", self)
        self.private_chat_button.clicked.connect(self.open_private_chat_dialog)

        # Chat display (in the center)
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        
        self.chat_display_title = QLabel("Public Chat", self)
        self.chat_display_title.setStyleSheet("font-weight: bold; font-size: 16px;")

        # Message input (bottom)
        self.message_input = QLineEdit(self)
        self.message_input.returnPressed.connect(self.send_message)
        
        self.upload_button = QPushButton("Upload File", self)
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        # Side layout
        side_layout = QVBoxLayout()
        side_layout.addWidget(self.side_menu_title)
        side_layout.addWidget(self.private_chat_button)
        side_layout.addWidget(self.side_menu)
        side_layout.setStretch(4, 1)
        main_layout.addLayout(side_layout)

        # Chat layout
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_display_title)
        chat_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.upload_button)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        main_layout.addLayout(chat_layout)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 4)

        self.websocket_thread = WebsocketConnection(self)
        self.websocket_thread.start()

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.websocket_thread.send_message(message)
            self.message_input.clear()

    def display_message(self, message):
        self.chat_display.append(message)

    def open_private_chat_dialog(self):
        dialog = PrivateChatDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_users = dialog.result
            if selected_users:
                # Add the private chat with multiple users to the side menu
                chat_name = f"Private Chat with {', '.join(selected_users)}"
                self.side_menu.addItem(chat_name)
                print(f"Private chat initiated with: {', '.join(selected_users)}")

    def change_chat(self, item):
        selected_chat = item.text()
        self.chat_display_title.setText(selected_chat)
        # Clear the chat display for now (you can modify it to display chat history)
        self.chat_display.clear()
        print(f"Switched to {selected_chat}")


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
        global ONLINE_USERS
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
                        msg, type = ParseInMessage(message)
                        if type == "client_list":
                            ONLINE_USERS = msg
                            print("Online Users:")
                            print(ONLINE_USERS)
                            print()
                            continue  
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

    async def websocket_send(self, message):
        if self.connected and self.websocket:
            await self.websocket.send(message) 


app = QtWidgets.QApplication(sys.argv)
window = G40chatApp()
window.showMaximized()

window.websocket_thread.message_received.connect(window.display_message)

sys.exit(app.exec_())
