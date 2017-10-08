from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from pathlib import Path


# Test if the key file exists
key_file_name = "mykey.pem"
key_file = Path(key_file_name)
if key_file.exists():
    # Open a new key file
    print("A key file is found. Load the key")
    f = open(key_file_name,'rb')
    private_key = RSA.importKey(f.read())
    f.close()
else:
    # Generate Pub/Priv Key
    print("There is no key file. Create a new one")
    random_generator = Random.new().read
    private_key = RSA.generate(1024,random_generator)
    
    # Export private key
    f = open(key_file_name,'wb')
    f.write(private_key.exportKey('PEM'))
    f.close()

# Sign data via private key
text = "abcdefg".encode("UTF-8")
hash = SHA256.new(text).digest()
signature = private_key.sign(hash,'')



#Import key
f = open(key_file_name,'br')
import_private_key = RSA.importKey(f.read())
f.close()

#Derive public key
public_key = import_private_key.publickey()

# Verify Key
print(public_key.verify(hash,signature))
