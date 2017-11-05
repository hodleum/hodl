from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.MD5 as MD5
from Crypto.Hash import SHA

# todo: all keys must be str
def h(s):
    """Hash"""
    return str(MD5.new(bytes(str(s), 'utf-8')).digest())

def gen_keys():
    """Generates keys"""
    # todo: написать генерацию ключей (privatekey, publickey - str)
    return privatekey, publickey

def sign(plaintext, priv_key):
    """Creates signature"""
    plaintext = bytes(plaintext,'utf8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return signature

def verify_sign(sign, plaintext, pub_key):
    """Verifies signature"""
    plaintext = bytes(plaintext,'utf8')
    # decryption signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, sign)
    return test
