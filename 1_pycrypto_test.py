from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(1024,random_generator)
public_key = key.publickey()
text = "abcdefg"
hash = SHA256.new(text).digest()
signature = key.sign(hash,'')
print(public_key.verify(hash,signature))
