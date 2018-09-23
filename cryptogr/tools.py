from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.MD5 as MD5
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_OAEP
import base64


def h(s):
    """Hash"""
    return ''.join([str(e) for e in list(MD5.new(bytes(str(s), 'utf-8')).digest())])


def gen_keys():
    """
    Generates keys
    :return: (private key, public key)
    """
    privatekey = RSA.generate(2048)
    publickey = privatekey.publickey()
    return privatekey.exportKey().decode(), publickey.exportKey().decode()


def sign(plaintext, private_key):
    """
    Creates signature

    :param plaintext: text
    :type plaintext: str

    :param private_key: RSA private key
    :type private_key: str

    :return: str
    """
    # todo: use pukey hashes in transaction and smart contracts' author fields and store public key in sign
    priv_key = RSA.importKey(private_key)
    plaintext = plaintext.encode('utf-8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return base64.encodebytes(signature).decode()


def sign_block(plaintext, private_key):
    """
    Creates signature

    :param plaintext: text
    :type plaintext: str

    :param private_key: RSA private key
    :type private_key: str

    :return: str
    """
    # todo: use pukey hashes in transaction and smart contracts' author fields and store public key in sign
    priv_key = RSA.importKey(private_key)
    plaintext = plaintext.encode('utf-8')
    # creation of signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(priv_key)
    signature = signature.sign(myhash)
    return base64.encodebytes(signature).decode()


def verify_block(s, plaintext, public_key, bch):
    """
    Verifies signature

    :param s: signature
    :type s: str

    :param plaintext: text
    :type plaintext: str

    :param public_key: RSA public key
    :type public_key: str

    :param bch: Blockchain
    :type bch: Blockchain

    :return: bool
    """
    if public_key[-1] == ']':
        return bch.verify_sc_sign(public_key, s)
    pub_key = RSA.importKey(public_key)
    plaintext = plaintext.encode('utf-8')
    # decryption signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, base64.decodebytes(s.encode()))
    return test


def verify_sign(s, plaintext, public_key, bch):
    """
    Verifies signature

    :param s: signature
    :type s: str

    :param plaintext: text
    :type plaintext: str

    :param public_key: RSA public key
    :type public_key: str

    :param bch: Blockchain
    :type bch: Blockchain

    :return: bool
    """
    if public_key[-1] == ']':
        return bch.verify_sc_sign(public_key, s)
    pub_key = RSA.importKey(public_key)
    plaintext = plaintext.encode('utf-8')
    # decryption signature
    myhash = SHA.new(plaintext)
    signature = PKCS1_v1_5.new(pub_key)
    test = signature.verify(myhash, base64.decodebytes(s.encode()))
    return test


def encrypt(plaintext: str, pub_key: str) -> str:
    """
    Encrypt text with RSA
    """
    key = RSA.importKey(pub_key)
    encrypter = PKCS1_OAEP.new(key)

    plaintext = plaintext.encode()
    size = key.size_in_bytes()
    ciphertext = b''
    for i in range(0, len(plaintext) // (size - 42) + 1):
        block = plaintext[i * (size - 42):(i + 1) * (size - 42)]
        ciphertext += encrypter.encrypt(block)
    return base64.encodebytes(ciphertext).decode()


def decrypt(text: str, priv_key: str) -> str:
    """
    Decrypt ciphertext with RSA
    """
    key = RSA.importKey(priv_key)
    text = base64.decodebytes(text.encode())
    decrypter = PKCS1_OAEP.new(key)
    size = key.size_in_bytes()

    plaintext = b''
    for i in range(0, len(text) // size):
        block = text[i * size: (i + 1) * size]
        plaintext += decrypter.decrypt(block)
    return plaintext.decode()


if __name__ == '__main__':
    priv, pub = gen_keys()
    print(decrypt(encrypt('test', pub), priv))
