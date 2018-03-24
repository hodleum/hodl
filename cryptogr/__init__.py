"""Cryptography module for HODL
h(s:str) is a hash function (output: hash of this string(str))
gen_keys() generates private and public keys(output:private key(bytes), public key(bytes))
sign(plaintext:str, private_key:bytes) signs plaintext(output:sign(bytes))
verify_sign(sign:bytes, plaintext:str, public_key:bytes) checks if sign is valid (output: is sign valid(bool))"""
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.MD5 as MD5
from Crypto.Hash import SHA
from Crypto.Cipher import DES


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


def encrypt_text(plaintext, key):
    plaintext = str(plaintext)
    l = len(plaintext)
    while len(plaintext) % (len(key)-1):
        plaintext += ' '
    plaintext = str(len(plaintext)-l)+';'+plaintext
    plaintext = plaintext.encode()
    des = DES.new(key, DES.MODE_ECB)
    return des.encrypt(plaintext)


def decrypt_text(text, key):
    des = DES.new(key, DES.MODE_ECB)
    text = des.decrypt(text).decode()
    i = int(text.split(';')[0])
    text = ';'.join(text.split(';')[1:])
    text = text[:-i-1]
    return text
