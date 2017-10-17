import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode


global f
f = ['priv.key', 'pub.key']

def h(s):    # Хэш, МЕНЯТЬ НИНАДА
    return MD5.new(bytes(str(s), 'utf-8')).digest()


def keys():    # возвращает ключи, примерно правильно
    return RSA.importKey(open(f[0], "r").read()).exportKey(), RSA.importKey(open(f[1], "r").read()).exportKey()


def genkeys():  # генерирует приватный и открытый ключи, пишет их в файлы f[0] и f[1]
    keys = RSA.generate(1024)
    f1 = open(f[0], 'wb')
    f2 = open(f[1], 'wb')
    f1.write(keys.exportKey())  # write private key
    f2.write(keys.publickey().exportKey())  # write public key


def sign(data, key='my key'):    # подписывает data (тип str) секретным ключом key (тип str).
    # Если key == 'my key', подписывает ключом из f[0]
    # Возвращает подпись (тип str)
    # ВАЖНО: verify_str должна нормально работать с подписью, которую дает эта функция
    if key =='my key':
        key = open(f[0], "r").read()
    data = bytes(data, 'utf-8')
    rsakey = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    # It's being assumed the data is base64 encoded, so it's decoded before updating the digest
    digest.update(data)
    sign = signer.sign(digest)
    return b64encode(sign)


def verify_sign(signature, data, pub_key):  # проверяет, подписал ли pub_key(тип str) data(тип str) и получил signature
    #try:
    rsakey = RSA.importKey(pub_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(b64decode(data))
    if signer.verify(digest, b64decode(signature)):
        return True
    #except:
    #    pass
    #print('exception')
    return False
