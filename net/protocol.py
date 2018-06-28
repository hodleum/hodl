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


def generate(message="", type="", peers=set(), pubkeys=tuple(), encoding="text", full=True,
             endaddr="", DISABLE_TEST=False):
    """
    Generate message for HSock
    :param message: str
    :param type: str, type of message
    :param peers: Peers, my peers
    :param pubkeys: list, my pubkeys
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

    # Message generation

    if type not in info.SUPPORTED_TYPES and not DISABLE_TEST:
        raise Exception("Not Supported Type. To disable test set DISABLE_TEST to True")
    if encoding not in info.SUPPORTED_ENCODINGS and not DISABLE_TEST:
        raise Exception("Not Supported Encoding. To disable test set DISABLE_TEST to True")
    mes = {}
    mes["type"] = type
    if endaddr is not None:
        mes["address"] = endaddr
    mes["encoding"] = encoding
    mes["body"] = message
    res["message"] = mes
    return json5.dumps(res, indent=5)


def handle(answer, adr, mypeers=set()):
    """
    Handle message answer from adr
    :param answer: str, message
    :param adr: str, sender's address
    :param mypeers: Peers
    :return: request_peers: list, list of peers' hashes to request
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

    if rlength:
        request_peers = mypeers.needed_peers(answer.get('peers'))
    else:
        request_peers = []
    return request_peers


if __name__ == "__main__":
    from net.Peers import Peers
    log.basicConfig(level=log.DEBUG)
    print(handle(generate(message="Hello World!", pubkeys=[], type="PRequest", peers=Peers()), "0xEXAMPLE",
                 mypeers=set()))
