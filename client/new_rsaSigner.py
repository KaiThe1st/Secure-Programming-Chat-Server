from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


PEM_HEADER_PUBK = "-----BEGIN PUBLIC KEY-----"
PEM_FOOTER_PUBK = "-----END PUBLIC KEY-----"
CHOSEN_HASH = hashes.SHA256()


def rsaSign(message) -> bytes:
    with open("private_key_pem_pass.txt", "rb") as file:
        pwd = file.read()

    with open("./private_key.pem","rb") as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password = pwd,
            )
    assert isinstance(private_key, rsa.RSAPrivateKey) == True
    if isinstance(message, bytes):
        pass
    if isinstance(message, str):
        message = message.encode()
    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(CHOSEN_HASH),
                salt_length=32
            ),
            CHOSEN_HASH
        )
    except Exception as e:
        raise ValueError(f"Signing failed: {e}")

    return signature


def rsaVerify(message, signature, pub_key) -> bool:
    if (pub_key.find(PEM_FOOTER_PUBK) == -1 or pub_key.find(PEM_HEADER_PUBK) == -1):
        pub_key = pub_key.replace(PEM_FOOTER_PUBK,"").replace(PEM_HEADER_PUBK,"").strip()
        pub_key = PEM_HEADER_PUBK + '\n' + pub_key + '\n' + PEM_FOOTER_PUBK
    
    if isinstance(pub_key, bytes):
            public_key = serialization.load_pem_public_key(pub_key)
    elif isinstance(pub_key, str):
            public_key = serialization.load_pem_public_key(pub_key.encode())
    else: 
        return False  
            
    assert isinstance(public_key, rsa.RSAPublicKey) == True 
    
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(CHOSEN_HASH),
                salt_length=32)
        , 
        CHOSEN_HASH)
    except Exception as e:
        # raise e
        return False
    return True

#for testing this module seperately from the main program
if __name__ == "__main__":
    msg = "hello".encode()
    signature = rsaSign(msg)
    with open("public_key.pem", "rb") as f:
        pub_k = f.read()
        
    if (rsaVerify(msg, signature, pub_k)):
        print("verified")
