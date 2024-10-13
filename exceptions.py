class GreedyPetException(Exception):
    def __init__(self, message: str, info: str = None):
        self.info = info
        super().__init__(message)


class NotSupported(GreedyPetException):
    pass
