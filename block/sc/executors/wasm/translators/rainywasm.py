"""
It's rainy today, isn't it? 61 48 52 30 63 48 4d 36 4c 79 39 70 59 6d 49 75 59 32 38 76 61 31 68 78 51 55 4e 6d
"""
from ppci import wasm
from sc_api import hdlib
from threading import Thread



class WasmProcess:
    def __init__(self, prg, backend="ppci", platform="python"):
        self.prg = wasm.Module(prg)
        self.backend = backend

    def run_script(self) -> Thread:
        loaded = wasm.instantiate(self.prg, hdlib.pyimports, "python")
        print(str(loaded.exports._function_map))
        thr = Thread(target=loaded.exports.main, daemon=True)
        thr.run()
        return thr

    def __str__(self):
        pass

    def from_json(self):
        pass

if __name__ == '__main__':
    inst = WasmProcess("(module (func (export main) (result i32) (i32.const 42) (return)))")