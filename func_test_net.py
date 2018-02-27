import sys
import block
import cryptogr as cg


#Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
#After that Alice creates transaction & sends it to Bob & Chuck(they all are waiting while net.py is doing it)
#Two seconds later Bob creates block & sends it to Alice & Chuck
bch = block.Blockchain()

name = sys.argv[0]
