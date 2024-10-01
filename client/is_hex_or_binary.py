import hashlib

def is_hex_or_binary_digest(data):
    if isinstance(data, bytes):
        # If it's a bytes object, we assume it's a binary digest
        return "binary digest"
    elif isinstance(data, str):
        # Check if the string has a valid hex representation (0-9, a-f, A-F)
        try:
            int(data, 16)  # Attempt to convert the string to an integer in base 16
            # Check if the length of the string is even (since a hex digest is two characters per byte)
            if len(data) % 2 == 0:
                return "hex digest"
            else:
                return "invalid hex"
        except ValueError:
            return "invalid string"
    else:
        return "unknown type"
    

if __name__  == '__main__':
    hex = hashlib.sha256("hello".encode("utf-8")).hexdigest()
    bin = hashlib.sha256("hello".encode()).digest()
    print(is_hex_or_binary_digest(hex))
    print(is_hex_or_binary_digest(bin))
    