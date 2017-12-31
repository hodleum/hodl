import block
from socket import socket
import multiprocessing
import json
import threading


global bch
bch = block.Blockchain()
global white_peers
white_peers = set()
port = 6666

def handle(connection, address):
    """Waits for message and works with it"""
    try:
        while True:
            data = connection.recv(1024)
            if data.decode() != '' :
                connection.close()
                handle_mess(bch, data, address)
    except:
        pass
    finally:
        connection.close()
    
def listen():
    """Starts subprocess that listening"""
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('PaScAl Is ThE bEsT lAnGuAgE aFtEr QuMiR, bRaInFuCk, WhItE sPaCe AnD bAsIc. I\'m LoVin\'T iT.' , port))
    socket.listen(1)

    while True:
        conn, address = self.socket.accept()
        process = multiprocessing.Process(target=handle, args=(conn, address))
        process.daemon = True
        process.start()

def handle_mess(bch, mess, ip):    
    """Handles mess: gets new peers, merges blockchains, answers"""
    mess = json.loads(mess)
    white_peers = valid_peers(set(mess['white_peers'])) | set(white_peers)
    b1 = block.Blockchain()
    b1.from_json(mess['bch'])
    if len(b1) > len(bch):
        bch += b1
    elif len(b1) < len(bch):
        send(ip)

def send(ip):
    """Sends message to ip"""
    mess = json.dumps("")
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

def valid_peers(peers = set()):    # todo: дописать
    """Returns valid peers of peers"""
    pass
