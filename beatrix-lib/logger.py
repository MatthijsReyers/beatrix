from typing import List
import traceback

ASCII_RED = '\u001b[31m'
ASCII_YELLOW = '\u001b[31m'
ASCII_RESET = '\u001b[0m'

WARN_LEVEL = 3
LOG_LEVEL = 2

class Logger():
    def __init__(self):
        self._callbacks: List[(int, callable)] = []

    def on_message(self, callback: callable):
        self._callbacks.append(callback)

    def exception(self, e:Exception, location:str=None):
        """ Logs an unexpected exception with optionally a note about its location.
        
        Arguments:
            e (Exception): The exception to log
            location (str): Optional hint/note about the location that calls this function.
        """
        message = f'[{ASCII_RED}${ASCII_RESET}] An unexpected \'{ASCII_RED}{type(e)}{ASCII_RESET}\' '
        message += 'error occurred ' + (f'in \'{location}\':' if location != None else ':')
        for (_, callback) in self._callbacks:
            callback(message)
        print(message)
        traceback.print_exc()

    def warn(self, message:str):
        message = f'[{ASCII_YELLOW}!{ASCII_RESET}] '+message
        for (level, callback) in self._callbacks:
            if level >= WARN_LEVEL:
                callback(message)
        print(message)

    def log(self, message:str):
        print('[*] '+message)

    def okay(self, message:str):
        print('[*]')
