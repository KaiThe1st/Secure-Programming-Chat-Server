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

<<<<<<< Updated upstream
=======
with open("./server_info.json", 'r') as server_info:
        data = json.load(server_info)
        ip = data["master_server_ip"]
        port = data["master_server_port"]

SERVER_ADDRESS = f'{ip}:{port}'


class UploadDialog(QDialog):
    global SERVER_ADDRESS
    def __init__(self):
        super(UploadDialog, self).__init__()

        self.setWindowTitle('File Upload')
        self.setGeometry(150, 150, 400, 300)
        layout = QVBoxLayout()
        self.file_label = QLabel('Choose a file to upload first', self)
        self.status_label = QLabel('', self)
        self.upload_btn = QPushButton('Browser', self)
        self.upload_btn.clicked.connect(self.click_to_upload)
        layout.addWidget(self.file_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.upload_btn)

        self.setLayout(layout)
    def click_to_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "", 
                                                   "All Files (*);;Text Files (*.txt);;Images (*.png *.jpg *.jpeg)", 
                                                   options=QFileDialog.Options())
        if file_path:
            self.file_label.setText(f'Selected File: {file_path}')
            self.upload_file(file_path)

    def upload_file(self, file_path):
        api_url = f"http://{SERVER_ADDRESS}/api/upload"      
        files = {'file': open(file_path, 'rb')}
        try:
            response = requests.post(api_url, files=files)
            if response.status_code == 200:
                response_json = json.loads(response.text)
                file_url = response_json["body"]["file_url"]
                with open("./client_state.json", "r") as fin:
                    client_state = json.load(fin)
                if file_url not in client_state["file_urls"]:
                    client_state["file_urls"].append(file_url)
                with open("./client_state.json", "w") as fout:
                    json.dump(client_state, fout, indent=4)
                self.status_label.setText("File uploaded successfully!")
            else:
                self.status_label.setText(f"Failed to upload file: {response.status_code}")

        except Exception as e:
            self.status_label.setText(f"Error: {e}")

        finally:
            files['file'].close()


class DownloadDialog(QDialog):
    global SERVER_ADDRESS
    def __init__(self):
        super(DownloadDialog, self).__init__()

        self.setWindowTitle('File Donwload')
        self.setGeometry(150, 150, 550, 600)
        
        layout = QVBoxLayout(self)
        self.filelist = QListWidget(self)
        with open("./client_state.json", "r") as fin:
            files = (json.load(fin))["file_urls"]
            
        for file in files:
            self.filelist.addItem(file)
        self.filelist.itemClicked.connect(self.choose_file)    
        
        self.stored_loc_label = QLabel('Click Download first.', self)
        
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.download_file)
        
        layout.addWidget(self.filelist)
        layout.addWidget(self.stored_loc_label)
        layout.addWidget(self.download_button)
        layout.setStretch(0, 1)
        
        self.expectedfile = ""

    def choose_file(self, item):
        file_url = item.text()
        self.expectedfile = file_url
        print(file_url)
    
    def download_file(self):
        response = requests.get(self.expectedfile, stream=True)
        response.raise_for_status()
        filename = self.expectedfile.replace("/", "\\").split("\\")[-1]
        if response.status_code == 200:
            with open(f"./download/{filename}", 'wb') as fout:
                for chunk in response.iter_content(chunk_size=8192):
                    fout.write(chunk)
            self.stored_loc_label.setText(f"Downloaded successfully. The file is at ./download/{filename}")
        else:
            self.stored_loc_label.setText(f"Unsuccessful download.")


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
        with open("./client_state.json", "r") as file:
            data = json.load(file)
            people = data["NS"]
            for person_id, person_data in people.items():
                self.user_list.addItem(person_data["name"])

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

>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
=======
        self.cache_chat()

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
        
        display_fingerprint = ""     
        
        
        with open ("./client_state.json", "r") as client_state:
            client_state_data = json.load(client_state)  
        
        self.chat_display.clear()
        
        if selected_chat == "Public Chat":
            self.current_chat = "public_chat"
            self.current_mode = "public_chat"
        else:
            self.current_mode = "chat"
            self.current_chat = selected_chat
        
        for fp in client_state_data["NS"]:
            if client_state_data["NS"][fp]["name"] == selected_chat:
                display_fingerprint = fp
        
        if self.current_chat == "public_chat":
            display_fingerprint = "public_chat"
        if display_fingerprint in client_state_data["chat_history"]:
            self.chat_display.append(client_state_data["chat_history"][display_fingerprint])

        print(f"Switched to {selected_chat}")
        return display_fingerprint

    def cache_chat(self):
        client_state_data = {}   
        with open("./client_state.json", "r") as client_state:
            client_state_data = json.load(client_state)
            
            if self.current_chat == "public_chat":
                fingerprint = "public_chat"
            else:
                for fp in client_state_data["NS"]:
                    if client_state_data["NS"][fp]["name"] == self.current_chat:
                        fingerprint = fp
            client_state_data["chat_history"][fingerprint] = self.chat_display.toHtml()
        
        with open("./client_state.json", "w") as client_state:            
            json.dump(client_state_data, client_state, indent=4)
            
        # return client_state_data

    def upload_modal_open(self):
        dialog = UploadDialog()
        dialog.exec_() 
        
    def download_modal_open(self):
        dialog = DownloadDialog()
        dialog.exec_() 

        
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
=======
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

>>>>>>> Stashed changes
app = QtWidgets.QApplication(sys.argv)
window = G40chatApp()
window.showMaximized()

window.websocket_thread.message_received.connect(window.display_message)

sys.exit(app.exec_())