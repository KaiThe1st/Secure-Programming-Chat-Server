from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# added by Khanh - 13/10/2024

def generate_key_pair():
    # Generate a 2048-bit RSA key pair
    private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
    )
    
    with open("private_key_pem_pass.txt",'rb') as file:
        pwd = file.read()
    
    # Export the private key
    private_key_bytes = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.BestAvailableEncryption(pwd),
    )
    
    with open("private_key.pem",'wb') as file:
        file.write(private_key_bytes)
    
    # Export the public key
    public_key_bytes = private_key.public_key().public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    
    with open("public_key.pem",'wb') as file:
        file.write(public_key_bytes)

    # print("Keys generated successfully!")


#for testing this module seperately from the main program
if __name__ == "__main__":
    generate_key_pair()
