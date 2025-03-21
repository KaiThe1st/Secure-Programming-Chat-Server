
# GROUP 40 CHAT APP
Nathan Dang (a1794954@adelaide.edu.au) <br>
Haydn Gaetdke (a1860571@adelaide.edu.au) <br>
Quoc Khanh Duong (a1872857@adelaide.edu.au) <br>
Dang Hoan Nguyen (a1830595@adelaide.edu.au) <br>

# Dependencies
The dependencies are located within the requirement.txt file

# How to run the chat app
!!! IMPORTANT: please use powershell terminal because it needs to use the computer ports
1. Download relevant libraries within requirement.txt
```
pip install -r requirements.txt
```
2. Server
- Open a powershell terminal and navigate to server folder
```
cd server
```
- Run createFiles.py to create necessary files
```
python createFiles.py
```
- Run server.py (The server will only run if the necessary files are there)
```
python server.py
```
- After running server.py, if the public-private key pair is not created automatically, please run rsaKeyGenerator.py within server file
```
python rsaKeyGenerator.py
```
3. Client
- Open another powershell terminal and navigate into the client folder
```
cd client
```
- Run chatApp.py (You should see the public-private key pair being generated as well as the client_state.json and server_info.json). By default, the server_info.json will be localhost:8080
```
python chatApp.py
```
# How to chat 
1. Public chat
- Click to choose public chat on the left side menu. <br>
- Enter text into the text field at the bottom. <br>
- Press send button to send <br>
The message will appear on everybody's screen with the public chat attribute attached to it.
2. Private chat
- Choose a name on the left side menu (The name are randomly generated on each computer). <br> 
- Enter text into the text field at the bottom. <br>
- Press send button to send. The message will appear on your screen and the other person screen. <br>
3. Group chat
- Click "New Group Chat" on the top-left corner. <br>
- Choose who you want to create the group with and then click "Create" to create the group.
- The group will appear on the left hand side of the screen. <br>
- Choose the group to start chatting <br>
- Enter text into the text field at the bottom. <br>
- Press send button to send. The message will appear on your screen and be sent to the other people in the group. <br>
# How to test inter-server chat
- Modify the state["neighbours"] according to the state.example.json. <br>
- Modify the server_info.json if needed to connect to the right server. <br>
- Run two servers (on two different computers). <br>
- If the servers are successfully connected, take turn open the chat app on each client (with the server_info.json correctly configured). <br>
- If everything works, you can start sending messages by following the instructions above. <br>
# How to upload and download files
1. Upload a file
- Click "Upload File" at the bottom-right corner of the screen. <br>
- Click browse and choose ONE file to upload. A "File uploaded successfully" message will appear if the upload was successful. Failing to upload will generate a "Failed to upload file: [filename]" error message. <br>
2. Download a file
- Click "Download file" at the bottom-right corner of the screen. <br>
- Choose the URL of the file that you want to download and click "Download" to download. A "Downloaded successfully. The file is at path/to/filename" message will appear. <br>

# NOTE
if client isnt working, delete private_key.pem, public_key.pem, and client_state.json and re-run chatApp.py
To connect to another server, add that server information accodring to the state.example.json
