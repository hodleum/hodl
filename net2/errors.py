

class BaseError(Exception):
    message = 'Base error'
    code = '000'

    def __init__(self, *args):
        super().__init__(*args)
        self.message += ': ' + args[0]


class BadRequest(BaseError):
    message = 'Bad request'
    code = '001'


class UnhandledRequest(BaseError):
    message = 'Unhandled Request'
    code = '002'
