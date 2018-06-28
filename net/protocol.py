"""
HODL transport protocol
"""

import base64
import logging as log
import platform
import zlib

import json5

from net import info


def compress_b64(d2c, cspeed=-1):
    """
    Compressing message for hsock
    :param d2c: string
    :param cspeed: int
    :return: string
    """
    log.debug("COMPRESSION STARTED")

    d2c = base64.urlsafe_b64encode(d2c).encode("utf8")

    log.debug("PREVIOUS B64:", d2c)

    d2c = zlib.compress(d2c, level=cspeed)
    return base64.standard_b64encode(d2c)


def generate(message="", peers=(), ans=(), pubkeys=(), requests=(), encoding="text", full=True,
             endaddr="", disable_test=False):
    """
    Generate message for HSock
    :param message: str
    :param t: str, type of message
    :param peers: Peers, my peers
    :param pubkeys: list, my pubkeys
    :param requests: list, requests
    :param encoding: str, encoding for message
    :param length: str, full or short
    :param endaddr: str, address for encoding
    :param disable_test: bool
    :return: message: str
    """
    res = {
        'length': full
    }
    csys = platform.system()
    if disable_test:
        log.warning("DISABLE_TEST is enabled! This is UNSECURE!")
    if full:

        pj = {
            'Name': info.PNAME,
            'Version': info.VERSION,
            'STypes': info.SUPPORTED_TYPES,
            'SEncodings': info.SUPPORTED_ENCODINGS
        }

        res["protocol"] = pj

        cd = {
            'CSys': csys
        }
        res["client_details"] = cd
        res["peers"] = peers.hash_list()
        res["pubkeys"] = pubkeys

    if encoding not in info.SUPPORTED_ENCODINGS and not disable_test:
        raise Exception("Not Supported Encoding. To disable test set DISABLE_TEST to True")

    mes = {
        'answers': ans,
        'requests': requests,
        'address': endaddr if endaddr is not None else None,
        'encoding': encoding,
        'body': message,
    }
    res["message"] = mes
    return json5.dumps(res, indent=5)


def handle_request(request):
    pass  # todo


def handle(answer, adr, mypeers=set(), alternative_message_handlers=()):
    """
    Handle message answer from adr
    :param answer: str, message
    :param adr: str, sender's address
    :param mypeers: Peers
    :param alternative_message_handlers: list of functions
    :return:
    [
        new peers,

        mes, list of args for generating answer message:
        [
            '',
            requests=[{request: 'request_peers', body: request_peers: list, list of peers' hashes to request}
                ]
            ans=[
                    answers
                ]
            full
        ]
    ]
    """
    # todo: process sender's pubkeys
    z = None
    log.debug('protocol.handle: answer: ' + str(answer))
    if not answer:
        log.debug("Empty message in handle")
        return [False]
    answer = json5.loads(answer)
    print(answer)
    rlength = answer.get("length")
    if rlength:
        rprotocol = answer.get("protocol")
        log.debug("HProto version is " + rprotocol.get("Version"))
    else:
        rprotocol = None
    requests = []
    if rlength:
        request_peers = mypeers.needed_peers(answer.get('peers'))
        requests.append({'request': 'request_peers', 'body': request_peers})
    answers = []
    for request in answer["requests"]:
        for amh in alternative_message_handlers:
            a = amh(request)
            if a:
                continue
        answers.append(handle_request(request))
    return True, ['', requests, answers, False]


if __name__ == "__main__":
    from net.Peers import Peers

    log.basicConfig(level=log.DEBUG)
    print(handle(generate(message="Hello World!", pubkeys=[], type="PRequest", peers=Peers()), "0xEXAMPLE",
                 mypeers=set()))
