from Cryptodome.PublicKey import RSA


PASSPHRASE = "G40" 

def generate_key_pair():
    # Generate a 2048-bit RSA key pair
    key = RSA.generate(2048)

    # Export the private key
    private_key = key.export_key(passphrase=PASSPHRASE, pkcs=8, format="PEM",
                                 protection="PBKDF2WithHMAC-SHA512AndAES256-CBC",
                                 prot_params={'iteration_count':21000})

    with open("private_key.pem", "wb") as private_file:
        private_file.write(private_key)

    # Export the public key
    public_key = key.public_key().export_key()
    with open("public_key.pem", "wb") as public_file:
        public_file.write(public_key)

    print("Keys generated successfully!")


#for testing this module seperately from the main program
if __name__ == "__main__":
    generate_key_pair()
