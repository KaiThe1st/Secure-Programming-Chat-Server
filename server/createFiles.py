from new_rsaKeyGenerator import generate_key_pair
import os
import json


def createFiles():
    if (not(os.path.isfile("private_key.pem") and os.path.isfile("public_key.pem"))):
        generate_key_pair()
    
    if (not(os.path.isfile("state.json"))):
        with open('state.example.json', 'r') as f:
            server_state = json.load(f)
            server_state["neighbours"] = []
        with open('state.json', 'w') as f:
            json.dump(server_state, f, indent=4)
            
            

if __name__ == "__main__":
    createFiles()