"""Cryptography module for HODL
h(s:str) is a hash function (output: hash of this string(str))
gen_keys() generates private and public keys(output:private key(str), public key(str))
sign(plaintext:str, private_key:str) signs plaintext(output:sign(str))
verify_sign(sign:str, plaintext:str, public_key:str) checks if sign is valid (output: is sign valid(bool))"""

from .tools import *
