"""
HODL transport protocol
"""

import base64
import logging as log
import os
import platform
import random
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import json5
from net.Peers import Peers
from net import info


def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)


def generate(message="", type="", peers=Peers(), pubkeys=tuple(), encoding="text", ctype="desktop", length="full",
             endaddr=None, DISABLE_TEST=False):
    """
    Generate message for HSock
    :param message: str
    :param type: str, type of message
    :param peers: Peers, my peers
    :param pubkeys: list, my pubkeys
    :param encoding: str, encoding for message
    :param ctype: str, platform type
    :param length: str, full or short
    :param endaddr: str, address for encoding
    :param DISABLE_TEST: bool
    :return: message: str
    """
    res = {}
    res["length"]=length
    csys = platform.system()
    if DISABLE_TEST:
        log.warning("DISABLE_TEST is enabled! This is UNSECURE!")
    log.debug(" Platform is "+str(csys))
    if length == "full":
        pj = {}
        pj["Name"] = info.PNAME
        pj["Version"] = info.VERSION
        pj["STypes"] = info.SUPPORTED_TYPES
        pj["SEncodings"] = info.SUPPORTED_ENCODINGS
        res["protocol"] = pj
        cd = {}
        cd["CSys"] = csys
        cd["CType"] = ctype
        res["client_details"] = cd
    if length != "short":
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


def handle(answer, adr, mypeers=Peers()):
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
    if rlength == "full":
        rprotocol = answer.get("protocol")
        log.debug("HProto version is "+rprotocol.get("Version"))
    else:
        rprotocol = None

    if rlength != "short":
        request_peers = mypeers.needed_peers(answer.get('peers'))
    else:
        request_peers = []
    return request_peers


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    print(handle(generate(message="Hello World!", pubkeys=[], type="PRequest", peers=Peers()), "0xEXAMPLE",
                 mypeers=Peers()))
