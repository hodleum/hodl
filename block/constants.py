# total reward for PoW
pow_total = lambda bch: 10000   # todo: percent of total money
# total reward for PoK
pok_total = lambda bch: 10000   # todo: percent of total money
# maximum hash to be a miner (will be removed)
pow_max = 1000000000000000000000000000000000000
# mining reward (will be removed)
miningprice = [100]
# free code size in smart contract (symbols)
sc_base_code_size = 5000000
# price of maximal smart contract's memory per symbol
sc_memprice = 0.001
# price of smart contract's code per symbol
sc_code_price = 10**(-6)
# base price of smart contract
sc_price = 0.05
# available symbols for nick
nick_av = set([chr(i) for i in list(range(48, 58)) + list(range(97, 123))] + list('_-.'))
# minimal length of nick
nick_min = 5
# maximal length of nick
nick_max = 20
# new block is mined every {block_time} seconds
block_time = 120
# blockchain freeze before mining block time (seconds)
freeze = 5
# free memory size for smart contract (symbols)
sc_base_mem = 10000000
# maximum SC memory size one peer can store
one_peer_max_mem = 4000000
