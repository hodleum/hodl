# TODO: Destroy the Planet Express Deliver Empire!

from ppci import wasm
#from block.sc.executors.wasm.exceptions import WTFLangException

SUP_LANGS = ["wasm"]


def fp_r(fname):
    with open(fname) as f:
        return f.read()


def my_print(args: int) -> int:
    print(args)
    result = 0


def run(wsmc, pyimports={'env': {}}, restrictions=tuple(), *arguments, **keyargs):
    loaded = wasm.instantiate(wsmc, pyimports, "python")

    res = loaded.exports.Main()

    print(res)
    return res


def prep_code(code=fp_r("scex.wasm"), lang="wasm"):
    if lang.lower() not in SUP_LANGS:
        #raise WTFLangException("{} language are not supported yet. Sorry!".format(lang))
        raise BaseException("Lang not available")
    m = wasm.Module(code)
    return m


if __name__ == "__main__":
    run(prep_code())
