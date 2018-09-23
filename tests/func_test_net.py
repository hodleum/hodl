import os
import json
import multiprocessing
import time
import logging as log
from sync import handle


name = str(os.getenv('HODL_NAME'))
log.basicConfig(level=log.DEBUG, format='%(module)s:%(lineno)d:%(message)s')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
if name == 'Alice':
    # set public key and peers
    time.sleep(2)
if name == 'Bob':
    # set public key and peers
    pass
if name == 'Chuck':
    # set public key and peers
    pass
if name == 'Dave':
    # set public key and peers
    pass
port = 5000


def main():
    pass
    # todo: send and accept net messages


multiprocessing.Process(target=main).start()
handle.loop(my_keys,)
