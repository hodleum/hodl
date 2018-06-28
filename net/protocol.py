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


def generate(message="", peers=tuple(), ans=tuple(), pubkeys=tuple(), requests=set(), encoding="text", full=True,
             endaddr="", DISABLE_TEST=False):
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
    :param DISABLE_TEST: bool
    :return: message: str
    """
    res = {}
    res["length"] = full
    csys = platform.system()
    if DISABLE_TEST:
        log.warning("DISABLE_TEST is enabled! This is UNSECURE!")
    log.debug(" Platform is "+str(csys))
    if full:
        pj = {}
        pj["Name"] = info.PNAME
        pj["Version"] = info.VERSION
        pj["STypes"] = info.SUPPORTED_TYPES
        pj["SEncodings"] = info.SUPPORTED_ENCODINGS
        res["protocol"] = pj
        cd = {}
        cd["CSys"] = csys
        res["client_details"] = cd
    if full:
        res["peers"] = peers.hash_list()
        res["pubkeys"] = pubkeys
    if encoding not in info.SUPPORTED_ENCODINGS and not DISABLE_TEST:
        raise Exception("Not Supported Encoding. To disable test set DISABLE_TEST to True")

    mes = {}
    mes['answers'] = ans
    if endaddr is not None:
        mes["address"] = endaddr
    mes["encoding"] = encoding
    mes["body"] = message
    res["message"] = mes
    return json5.dumps(res, indent=5)


def handle_request(request):
    pass # todo


def handle(answer, adr, mypeers=set(), alternative_message_handlers=tuple()):
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
    z = None
    answer = json5.loads(answer)
    print(answer)
    rlength = answer.get("length")
    if rlength:
        rprotocol = answer.get("protocol")
        log.debug("HProto version is "+rprotocol.get("Version"))
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
    return ['', requests, answers, False]


if __name__ == "__main__":
    from net.Peers import Peers
    log.basicConfig(level=log.DEBUG)
    print(handle(generate(message="Hello World!", pubkeys=[], type="PRequest", peers=Peers()), "0xEXAMPLE",
                 mypeers=set()))
