from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

# key generation
privatekey = RSA.generate(2048)
publickey = privatekey.publickey()

def get_keys():
    return privatekey, publickey

def sign(plaintext, priv_key):
    plaintext = bytes(plaintext,'utf8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return signature

def verify_sign(sign, pub_key, plaintext) :
    # decryption signature
    publickey = pub_key
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, sign)
    return test
