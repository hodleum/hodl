# TODO: Destroy the Planet Express Deliver Empire!

from ppci import wasm
from block.sc.executors.wasm.exceptions import *

SUP_LANGS = ["wasm"]


def fp_r(fname):
    with open(fname) as f:
        return f.read()


def run(wsmc, pyimports={}, restrictions=tuple(), *arguments, **keyargs):
    loaded = wasm.instantiate(wsmc, pyimports)
    try:
        res = loaded.exports.result()
    except AttributeError:
        raise WrongResultVar
    print(res)
    return res


def prep_code(code=fp_r("scex.wasm"), lang="wasm"):
    if lang.lower() not in SUP_LANGS:
        raise WTFLangException("{} language are not supported yet. Sorry!".format(lang))
    m = wasm.Module(code)
    return m


if __name__ == "__main__":
    run(prep_code())
