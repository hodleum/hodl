"""
HODL Socket protocol
Main transport protocol
"""

import base64
import logging as log
import os
import platform
import random
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

import json5

import net.info as info


def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)

def generate(message="", type="", peers=tuple(), pubkeys=[], encoding="text", ctype="desktop", length="full", endaddr=None, DISABLE_TEST=False):
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
        res["peers"] = str(peers)
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



def handle(answer, adr):
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
        try:
            os.mkdir("peers_dump")
        except Exception as ex:
            log.debug("  Directory already exists or something went wrong. Exception here: ")
            log.warning(ex)
        with open("peers_dump/peers_a{adr}_{r}.json".format(adr=adr, r=random.randint(0, 1000000)), "w") as f:
            json5.dump(fp=f, obj={"peers":answer.get("peers")})
            f.close()
    if answer.get("message").get("type") == "PRequest":
        zipdir("peers_dump", "tdmp.zip")
        with closing(open("tdmp.zip", "rb")) as f:
            b = f.read()
        z = base64.b64encode(b)
        z = str(z)
        os.remove("tdmp.zip")
        z = generate(z, type="PReturn", encoding="base64", length="short")
    if z is not None:
        return z


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    peer = ["peers", "here"]
    print(handle(generate(message="Hello World!", pubkeys=[], type="PRequest" ,peers=tuple(peer)), "0xEXAMPLE"))
