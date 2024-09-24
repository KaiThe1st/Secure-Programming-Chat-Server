from datetime import datetime

def eventLogger (event, status, subject, additional_info):
    now = str(datetime.now())
    
    if not status:
        print(f"[{now}]: EROR HAPPENING")
        return

    if event == "closeConnection":
        if additional_info != "":
            print(f"[{now}]: CLIENT {subject} DISCONNECTED {additional_info}")
        else:
            print(f"[{now}]: CLIENT {subject} DISCONNECTED")
        return
        
    if event == "signed_data_hello":
        print(f"[{now}]: CLIENT {subject} CONNECTED")
        return
        
    if event == "signed_data_server_hello":
        print(f"[{now}]: SERVER {subject} CONNECTED")
        return
        
        
    if event == "signed_data_chat":
        print(f"[{now}]: RECV a message from {subject}")
        return
    
    if event == "client_list_request":
        print(f"[{now}]: {subject} requested online users")
        return
        
    if event == "serverGoOnline":
        print()
        print("-------------------------------------------------------------")
        print(f"[{now}]: Server [{subject}] goes online ({additional_info})")
        return
    
    if event == "serverGoOffline":
        print(f"[{now}]: Server [{subject}] goes offline")
        print("-------------------------------------------------------------")
        print()
        return
    