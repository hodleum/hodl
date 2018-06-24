"""
HODL Socket protocol
Main transport protocol
"""

import logging as log
import platform
import sys

import json5

import net.info as info


def generate(message="", type="", peers=tuple(), pubkeys=[], request="", encoding="text", ctype="desktop", length="full", DISABLE_TEST=False):
    res = {}
    csys = platform.system()
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
        res["peers"] = str(peers)
    res["pubkeys"] = pubkeys

    # Message generation

    if type not in info.SUPPORTED_TYPES and not DISABLE_TEST:
        raise Exception("Not Supported Type. To disable test set DISABLE_TEST to True")
    if encoding not in info.SUPPORTED_ENCODINGS and not DISABLE_TEST:
        raise Exception("Not Supported Encoding. To disable test set DISABLE_TEST to True")
    mes = {}
    mes["type"] = type
    mes["encoding"] = encoding
    mes["body"] = message
    mes["request"] = request
    return json5.dumps(res, indent=5)


def handle(answer):
    pass


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    peer = ["peers", "here"]
    print(generate(message="Hello World!", pubkeys=[], type="E2E-SmartContract", peers=str(peer)))
