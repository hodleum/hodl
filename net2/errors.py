

class BaseError(Exception):
    message = 'Unhandled error'
    code = '000'

    def __init__(self, *args):
        super().__init__(*args)
        if args:
            self.message += ': ' + str(args[0])


class BadRequest(BaseError):
    message = 'Bad request'
    code = '001'


class UnhandledRequest(BaseError):
    message = 'Unhandled Request'
    code = '002'


class CryptogrError(BaseError):
    message = 'Error in cryptography'
    code = '100'


class VerificationFailed(CryptogrError):
    message = 'Message verification failed'
    code = '101'


class DecryptionFailed(CryptogrError):
    message = 'Decryption failed'
    code = '102'
