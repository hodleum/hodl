from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.MD5 as MD5
from Crypto.Hash import SHA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import struct
import base64


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
    plaintext = plaintext.encode('utf-8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return base64.encodebytes(signature).decode()


def verify_sign(s, plaintext, public_key):
    """Verifies signature"""
    pub_key = RSA.importKey(public_key)
    plaintext = plaintext.encode('utf-8')
    # decryption signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, base64.decodebytes(s.encode()))
    return test


def encrypt_aes(plaintext, key):
    plaintext = struct.pack('>L', len(plaintext)) + plaintext.encode('utf-8') + b'\x00' * (
            16 - (len(plaintext) + 4) % 16)
    aes = AES.new(key)
    return base64.encodebytes(aes.encrypt(plaintext)).decode()


def decrypt_aes(text, key):
    aes = AES.new(key)
    plaintext = aes.decrypt(base64.decodebytes(text.encode()))
    text_len = struct.unpack('>L', plaintext[:4])[0]
    return plaintext[4:text_len + 4].decode('utf-8')


def encrypt(plaintext, pub_key):
    key = RSA.importKey(pub_key)
    session = get_random_bytes(32)
    enc_session = PKCS1_OAEP.new(key).encrypt(session)
    text = base64.decodebytes(encrypt_aes(plaintext, session).encode())
    return base64.encodebytes(enc_session + text).decode()


def decrypt(text, priv_key):
    key = RSA.importKey(priv_key)
    text = base64.decodebytes(text.encode())
    cipher_text = base64.encodebytes(text[(key.size() + 1) // 8:]).decode()
    session = PKCS1_OAEP.new(key).decrypt(text[: (key.size() + 1) // 8])
    return decrypt_aes(cipher_text, session)
