"""
It synchronizes blockchain between HODL peers.
Algorthm:
The first user sends last block and blockchain's length to the other.
The second user sends delta between their blockchains' lengths, and if his blockchain is longer, sends 1000 or less blocks to first user.
The first user sends blocks if his blockchain is longer.
User checks blocks he accepted by getting the same blocks from other users (get_many_blocks), and if |delta|>1000, gets missing blocks
"""
