# GROUP 40 CHAT APP
Nathan Dang
Haydn Gaetdke
Quoc Khanh Duong
Dang Hoan Nguyen

# Dependencies
located within the requirement.txt file

# How to run
1. download relevant libraries within requirement.txt - pip install -r requirement.txt
2. open a terminal and navigate to server folder - cd server
3. run rsaKeyGenerator.py within server - python rsaKeyGenerator.py
4. run server.py - python server.py
5. open another terminal and navigate into the client folder
6. update the server_info.json file in the client to the relevant ip of server
7. navigate to the cient folder
8. run chatApp.py - python chatApp.py

# NOTE
if client isnt working, delete private_key.pem, public_key.pem, and client_state.json and re-run chatApp.py
