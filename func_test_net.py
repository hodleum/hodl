import sys
import os
import block
import cryptogr as cg
from Crypto.PublicKey import RSA


#Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
#After that Alice creates transaction & sends it to Bob & Chuck(they all are waiting while net.py is doing it)
#Two seconds later Bob creates block & sends it to Alice & Chuck


bch = block.Blockchain()
name = os.getenv('HODL_NAME')
keys = [0, 1]
f = open(name + "Priv.key", "r")
keys[0] = RSA.importKey(f.read())
f.close()
f = open(name + "Pub.key", "r")
keys[1] = RSA.importKey(f.read())
f.close()
print(keys)
