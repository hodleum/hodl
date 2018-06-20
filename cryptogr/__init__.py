"""Cryptography module for HODL
h(s:str) is a hash function (output: hash of this string(str))
gen_keys() generates private and public keys(output:private key(bytes), public key(bytes))
sign(plaintext:str, private_key:bytes) signs plaintext(output:sign(bytes))
verify_sign(sign:bytes, plaintext:str, public_key:bytes) checks if sign is valid (output: is sign valid(bool))"""

from .tools import *
