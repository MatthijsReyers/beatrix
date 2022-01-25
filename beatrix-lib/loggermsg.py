
class LoggerMessage():
    def __init__(self, level:int, message:str, local:bool):
        self.level   = level
        self.message = message
        self.local   = local
