from Cryptodome.Signature import pss
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA


def rsaSign(message):
    with open("./private_key.pem","rb") as private_file:
        private_key = RSA.import_key(private_file.read(),passphrase="G40")
    hash = SHA256.new(message)
    try:
        signature = pss.new(private_key, salt_bytes=32).sign(hash)
    except (ValueError):
        raise ValueError("Invalid RSA key length")
    except (TypeError):
        raise TypeError("Key has no private half")

    return signature


def rsaVerify(message, signature, public_key):
    hash = SHA256.new(message)
    verifier = pss.new(public_key, salt_bytes=32)
    try:
        verifier.verify(hash, signature)
        return True
    except (ValueError):
        raise ValueError("Invalid signature")


if __name__ == "__main__":
    pass