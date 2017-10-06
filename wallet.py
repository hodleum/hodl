import block
import cryptogr as cg


cg.f = ['priv.key', 'pub.key']
block.cg.f = ['priv.key', 'pub.key']
conf = getconf()
if not conf:
    cg.genkeys()
myaddr = ''.join(str(cg.keys()[1]).split("\\n")[1:len(str(cg.keys()[1]).split("\\n"))-1])



