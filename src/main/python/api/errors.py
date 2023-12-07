from .app import app

from .props import *


class ClientError(Exception):

    def __init__(self, status_code: int, *args):
        super().__init__(*args)
        self.status_code = status_code


class ValidationError(ClientError):

    def __init__(self, *args):
        super().__init__(400, *args)


class ForbiddenError(ClientError):

    def __init__(self):
        super().__init__(403, "You are not authorized to perform the request action")


class NotFoundError(ClientError):

    def __init__(self, *args):
        super().__init__(404, *args)


class PreconditionFailedError(ClientError):

    def __init__(self, *args):
        super().__init__(412, *args)


class PreconditionRequiredError(ClientError):

    def __init__(self, *args):
        super().__init__(428, *args)


def error_body(code: str, message: str):
    return {CODE: code, MESSAGE: message}


@app.errorhandler(ClientError)
def handle_error(err: ClientError):
    return error_body(err.__class__.__name__, str(err)), err.status_code
