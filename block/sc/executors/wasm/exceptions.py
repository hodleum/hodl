class WTFLangException(BaseException):
    def __init__(self, text="K.I.S.S. Also do not use wasm-runner to run non-wasm code. "):
        self.txt = text

class WrongResultVar(AttributeError):
    def __init__(self, text="You should export result to 'result' variable! "):
        self.txt = text
