from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.MD5 as MD5
from Crypto.Hash import SHA

# todo: all keys must be str
def h(s):
    """Hash"""
    return ''.join([str(e) for e in list(MD5.new(bytes(str(s), 'utf-8')).digest())])

def gen_keys():
    """Generates keys"""
    privatekey = RSA.generate(2048)
    publickey = privatekey.publickey()
    return privatekey.exportKey().decode(), publickey.exportKey().decode()

def sign(plaintext, private_key):
    """Creates signature"""
    priv_key = RSA.importKey(private_key)
    plaintext = bytes(plaintext,'utf8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return signature

def verify_sign(sign, plaintext, public_key):
    """Verifies signature"""
    pub_key = RSA.importKey(public_key) 
    plaintext = bytes(plaintext,'utf8')
    # decryption signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, sign)
    return test
