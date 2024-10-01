import hashlib
from base64 import b64encode, b64decode
from binascii import hexlify, unhexlify

def hex_to_bin(data):
    if isinstance(data, bytes):
            assert len(data) == 32
            hexdigest = hexlify(data).decode()
            return hexdigest
    elif isinstance(data, str):
        assert len(data) == 64
        try:
            int(data, 16)  # Attempt to convert the string to an integer in base 16
            # Check if the length of the string is even (since a hex digest is two characters per byte)
            if len(data) % 2 == 0:
                return data
            else:
                raise ValueError("invalid hex")
        except:
            raise ValueError("invalid string")
            
            
    else:
        return "unknown type"
    
#for testing
if __name__  == '__main__':
    chat = {}
    chat["participants"] = []
    hex = b64encode(hashlib.sha256("hello".encode("utf-8")).hexdigest().encode()).decode()
    # print(hashlib.sha256("hello".encode("utf-8")).hexdigest())
    bin = b64encode(hashlib.sha256("hello".encode()).digest()).decode()
    # print(hashlib.sha256("hello".encode()).digest())
    # print(len(hashlib.sha256("hello".encode()).digest()))
    # print(len(hashlib.sha256("hello".encode()).hexdigest()))
    decoded_hex = b64decode(hex.encode())
    print(len(decoded_hex))
    decoded_bin = b64decode(bin.encode())
    print(len(decoded_bin))
    # print(decoded_bin)
    # print(decoded_hex)
    # print(hex_to_bin(decoded_hex))
    # print(hex_to_bin(decoded_bin))
    chat["participants"].append(hex)
    chat["participants"].append(bin)
    
    for i in range(len(chat["participants"])):
        decoded = b64decode(chat["participants"][i].encode('utf8'))
        print(decoded)
        try: 
            hex = decoded.decode('utf8')
            print(hex)
            chat["participants"][i] = hex_to_bin(hex)
            print("Decode hex")
        except UnicodeDecodeError:
            chat["participants"][i] = hex_to_bin(decoded)
            print("Decode binary")
            
    print(chat["participants"])
