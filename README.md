# GROUP 40 CHAT APP

Nathan Dang
Haydn Gaetdke
Quoc Khanh Duong
Dang Hoan Nguyen

# Dependencies

The dependencies required to run the chat app are located within the requirement.txt file

# How to run
!!! IMPORTANT: please use powershell terminal because it needs to use the computer ports
1. Download relevant libraries within requirement.txt 
```
pip install -r requirements.txt
```
2. Open a powershell terminal and navigate to server folder
``` 
cd server
```
3. Run server.py 
```
python server.py
```
4. After running server.py, if the public-private key pair is not created automatically, please run rsaKeyGenerator.py within server file
``` 	
python rsaKeyGenerator.py
```	
5. Open another powershell terminal and navigate into the client folder
```
cd client
```
6. update the server_info.json file in the client to the relevant ip of server according to the server_info.example.json
8. run chatApp.py 
```
python chatApp.py
```

# NOTE
if client isnt working, delete private_key.pem, public_key.pem, and client_state.json and re-run chatApp.py
```
To connect to another server, add that server information accodring to the state.example.json
```
