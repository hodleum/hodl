"""
It's rainy today, isn't it? 61 48 52 30 63 48 4d 36 4c 79 39 70 59 6d 49 75 59 32 38 76 61 31 68 78 51 55 4e 6d
"""
from multiprocessing import Process

from ppci import wasm

from sc_api import hdlib


class WasmProcess:
    def __init__(self, prg, backend="ppci", platform="python"):
        self.prg = wasm.Module(prg)
        self.backend = backend


    def run_script(self, params=[]) -> Process:
        loaded = wasm.instantiate(self.prg, hdlib.pyimports, "python")
        thr = Process(target=loaded.exports.main, args=params)
        thr.run()
        self.thr = thr
        self.instance = loaded
        return thr

    def __str__(self):
        pass

    def from_json(self):
        pass


    def get_mem_block(self, block: int, size: int):
        try:
          return self.instance.exports.memory.read(block, size)
        except AttributeError:
          print("Memory is not available")
          return None
    def get_self_diag(self):
        try:
            mem_info = str(self.instance._memories)
            minfo2 = self.instance.exports.memory
        except AttributeError:
            mem_info = []
            minfo2 = ""

        try:
            ms, me = self.instance.mem0_start, self.instance.mem_end
        except AttributeError:
            ms, me = "null", "null"
        diagnose = """
RainyWasm self-diagnostics by DanGSun v0.1
--------------------------
Memory:
    Memories: {0}
    Memory export: {3}
    Functions: {1}
    Mem0 Start & end: {4} - {5}
----
Dir's info:
    Instance: {2}        
        """.format(len(mem_info), list(self.instance.exports._function_map), self.instance, minfo2, ms, me)

        return diagnose

if __name__ == '__main__':
    test_prgs = [
        "(module (func (export main) (result i32) (i32.const 42) (return)))",

        """(module
 (table 0 anyfunc)
 (memory $0 1)
 (export "memory" (memory $0))
 (export "main" (func $main))
 (func $main (; 0 ;) (result i32)
  (i32.const 0)
 )
)

""","""
(module
 (table 0 anyfunc)
 (memory $0 1)
 (export "memory" (memory $0))
 (export "main" (func $main))
 (func $main (; 0 ;) (param $0 i32) (result i32)
  (i32.add
   (get_local $0)
   (i32.const -40)
  )
 )
)

""","""
(module
 (table 0 anyfunc)
 (memory $0 1)
 (data (i32.const 12) "\00\00\00\00")
 (export "memory" (memory $0))
 (export "main" (func $main))
 (func $main (; 0 ;) (param $0 i32) (result i32)
  (i32.store offset=12
   (i32.const 0)
   (i32.add
    (get_local $0)
    (i32.const -40)
   )
  )
  (i32.const 0)
 )
)

"""
    ]
    for i in test_prgs:
        inst = WasmProcess(i)
        try:
          inst.run_script()
        except TypeError:
          inst.run_script(params=[2])

        print(inst.get_self_diag())
        mvar = inst.get_mem_block(0, 64)
        if mvar is not None:
          print("ZBlock: ", mvar)
          try:
            if int.from_bytes(mvar, byteorder='big', signed=False) != 2-45: raise BaseException("Test failed: result is not -43")
          except ValueError:
            pass
        try:
           inst.thr.terminate()
        except AttributeError:
           print("Already Stopped...")