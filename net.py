import block
from socket import socket
import json
import threading


global bch
bch = block.Blockchain()
global white_peers
white_peers = set()
port = 6666

def new_listen_thread():    # todo: дописать
    """listens in thread, handles mess, returns mess"""
    pass

def listen():
    """Listens for message, returns tuple (ip, mess)"""
    sock_listen = socket()
    sock_listen.listen(1)
    conn, ip = sock_listen.accept()
    data = conn.recv(4096)
    mess = str(data)
    summary_tuple = (ip, mess)
    return summary_tuple

def handle_mess(mess, ip):    # todo: дописать
    """Handles mess: gets new peers, merges blockchains, answers"""
    mess = json.loads(mess)
    white_peers = valid_peers(set(mess['white_peers'])) | set(white_peers)
    b1 = block.Blockchain()
    b1.from_json(mess['bch'])
    bch += b1

def send(ip, mess):
    """Sends mess to ip"""
    mess = json.dumps(mess)
    mess['white_peers'] = white_peers
    mess['bch'] = str(bch)
    sock_send = socket()
    sock_send.connect((ip, port))
    sock_send.send(mess)


def is_my_ip_white():    # todo: дописать
    """Checks if this computer's IP is white"""
    pass


def is_ip_white(ip):    # todo: дописать
    """Checks if ip is white"""
    pass

def valid_peers(peers=set()):    # todo: дописать
    """returns valid peers of peers"""
    pass
