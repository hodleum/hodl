"""
HODL transport protocol
"""

import base64
import logging
import platform
import zlib
import random
import json5
from net import info

log = logging.getLogger(__name__)


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
             endaddr="", mtype="AvailabilityPing", disable_test=False):
    """
    Generate message for HSock
    :param message: str
    :param peers: peers object
    :param ans: tuple
    :param pubkeys: tuple, my pubkeys
    :param requests: tuple, requests
    :param encoding: str, encoding for message, default value is text
    :param full: bool, full or short
    :param endaddr: str, address for encoding
    :param mtype: str, type of message
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
            'SEncodings': info.SUPPORTED_ENCODINGS
        }

        res["protocol"] = pj

        cd = {
            'CSys': csys
        }
        res["client_details"] = cd
        res["pubkeys"] = pubkeys

    if encoding not in info.SUPPORTED_ENCODINGS and not disable_test:
        raise TypeError("Not Supported Encoding. To disable test set DISABLE_TEST to True")
    if mtype not in info.SUPPORTED_TYPES and not disable_test:
        raise TypeError("Not Supported Type. To disable test set DISABLE_TEST to True")

    mes = {
        'address': endaddr if endaddr is not None else None,
        'encoding': encoding,
        'body': message,
        'type': mtype
    }
    if full:
        res["peers"] = peers.hash_list()
    res['n'] = random.randint(0, 1000)
    res['answers'] = ans
    res['requests'] = requests
    log.debug('n: %s requests: %s' % (res['n'], requests))
    res["message"] = mes
    return json5.dumps(res, indent=5)


def handle_request(request, peers):
    if request['request'] == 'peer_by_hash':
        ans = [peers.peer_by_hash(h) for h in request['body']]
        log.debug('Answer %s for %s request' % (ans, request))
        return ans


def handle_peer_ans(ans, peers):
    return peers   # todo


def handle(answer, adr, mypeers, alternative_message_handlers=(), alternative_answer_handlers=(), first=False):
    """
    Handle message answer from adr
    :param answer: str, message
    :param adr: str, sender's address
    :param mypeers: Peers
    :param alternative_message_handlers: list of functions
    :param alternative_answer_handlers: list of functions
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
    if not answer:
        log.debug("Empty message in handle")
        return [False]
    answer = json5.loads(answer)
    rlength = answer.get("length")
    log.debug('n: %s requests: %s,\npeers: %s' % (answer['n'], answer['requests'], answer.get('peers'))
              + ',\nlength: ' + str(rlength) + ',\nkeys: ' + str(answer.keys()))
    if rlength:
        rprotocol = answer.get("protocol")
    else:
        rprotocol = None
    requests = []
    if rlength:
        request_peers = mypeers.needed_peers(answer.get('peers'))
        log.debug('Requests appended by peer request')
        requests.append({'request': 'request_peers', 'body': request_peers})
    answers = []
    for request in answer["requests"]:
        log.debug('handle request: ' + str(request))
        for amh in alternative_message_handlers:
            a = amh(request)
            if a:
                answers.append(a)
                break
        else:
            answers.append(handle_request(request, mypeers))
    log.debug('Answers: %s' % answers)
    for ans in answer['answers']:
        for aah in alternative_answer_handlers:
            a = aah(ans)
            if a:
                break
        else:
            mypeers = handle_peer_ans(ans, mypeers)
    return answers or requests or first, ['', requests, answers, False, mypeers, answer['n']]


if __name__ == "__main__":
    from net.peers import Peers

    print(handle(generate(message="Hello World!", pubkeys=[], mtype="PRequest", peers=Peers()), "0xEXAMPLE",
                 mypeers=Peers()))
