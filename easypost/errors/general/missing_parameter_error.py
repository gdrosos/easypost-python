from easypost.errors import EasyPostError


class MissingParameterError(EasyPostError):
    def __init__(self, message: str):
        super().__init__(message=message)
