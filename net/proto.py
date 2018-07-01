from socket import socket
import logging as log
import struct


def sock_to(addr):
    sock = socket()
    sock.connect(addr)
    return sock


def recv(sock):
    """
    Receive function for socket connections

    :type sock: socket
    :return: data (bytes)
    """
    chunk = sock.recv(4)
    if len(chunk) < 4:
        return
    log.debug('proto.recv')
    slen = struct.unpack('>L', chunk)[0]
    chunk = sock.recv(slen)
    while len(chunk) < slen:
        chunk += sock.recv(slen - len(chunk))
    return chunk


def send(sock, data):
    """
    Send function for socket connections

    :type sock: socket

    :param data: data to send
    :type data: bytes, str

    :return: None
    """
    log.debug('proto.send')
    if type(data) == str:
        data = data.encode()
    data = struct.pack('>L', len(data)) + data
    sock.send(data)
