"""
It's rainy today, isn't it? 61 48 52 30 63 48 4d 36 4c 79 39 70 59 6d 49 75 59 32 38 76 61 31 68 78 51 55 4e 6d
"""
from ppci import wasm
from sc_api import hdlib
from threading import Thread

wasm.Memory

class WasmProcess:
    def __init__(self, prg, backend="ppci", daemon=True, platform="python"):
        self.prg = wasm.Module(prg)
        self.backend = backend
        self.daemon = daemon


    def run_script(self) -> Thread:
        loaded = wasm.instantiate(self.prg, hdlib.pyimports, "python")
        print(str(loaded.exports._function_map))
        thr = Thread(target=loaded.exports.main, daemon=self.daemon)
        thr.run()
        self.thr = thr
        self.instance = loaded
        return thr

    def __str__(self):
        pass

    def from_json(self):
        pass

    def get_self_diag(self):
        diagnose = """
RainyWasm self-diagnostics by DanGSun v0.1
--------------------------
Memory:
    Memories: {0}
    Functions: {1}
----
Dir's info:
    Instance: {2}        
        """.format(self.instance._memories, list(self.instance.exports._function_map), dir(self.instance))

        return diagnose

if __name__ == '__main__':
    inst = WasmProcess("(module (func (export main) (result i32) (i32.const 42) (return)))", daemon=False)
    inst.run_script()
    print(inst.get_self_diag())