from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_SNDBUF, SOL_SOCKET, SHUT_RDWR
from threading import Thread, Condition, Lock
from logger import Logger
import time

SEND_TIMEOUT = 0.8
RECV_TIMEOUT = 1.5
RECONNECT_TIME = 0.5

class StableSocket():
    def __init__(self, ip_addr:str, port:int, logger=None):
        self.ip_addr = ip_addr
        self.port    = port

        self.logger = Logger() if logger == None else logger
        
        self.reconnecting = False
        self.connected    = False
        self.on_connected = Condition()
        
        self._socket_mutex = Lock()
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(RECV_TIMEOUT)

        self.closed_by_user = False
        self._callbacks = []

    def connect(self):
        self.reconnect_thread = Thread(
            target=self.__reconnect_thread, 
            args=(), daemon=True)
        self.reconnect_thread.start()

    def close(self):
        """ Closes the socket  """
        self.closed_by_user = True
        self._socket.shutdown(SHUT_RDWR)
        self._socket.close()

    def send(self, data) -> bool:
        """ Tries to send data though the socket, if the socket is disconnected it will wait 
        `SEND_TIMEOUT` seconds for the socket to reconnect and otherwise it return `False` to 
        indicate the failure.

        Arguments:
            data (bytes/str): The data to send through the socket connection.

        Returns:
            True when data was successfully sent and False if not.
        """
        try: 
            if not self.connected:
                self.on_connected.acquire()
                self.on_connected.wait(timeout=SEND_TIMEOUT)
                self.on_connected.release()
            if self.connected:
                self._socket_mutex.acquire()
                self._socket.sendall(data)
                return True
        except BrokenPipeError:
            self.__set_connected(False)
        except Exception as e:
            print('[!] Found unexpected exception:\n', type(e), e)
        finally:
            if self._socket_mutex.locked():
                self._socket_mutex.release()
        return False

    def receive(self, buffer_size=1024) -> (bool, bytes):
        """ Tries to receive a buffer of 1024 bytes or a given size worth of data. If any data is 
        received it will return it in a tuple prepended with `True`, if it fails to receive data; 
        either through an error or timeout it will return `False` and an empty byte array.

        Arguments:
            buffer_size (int): The maximum amount of bytes to recieve (defaults to 1024).

        Returns:
            (True, data) when data was successfully sent and (False, '') when not.
        """
        try:
            self._socket_mutex.acquire()
            data = self._socket.recv(buffer_size)
            return (True, data)
        except ConnectionResetError:
            self.__set_connected(False)
        except OSError:
            self.__set_connected(False)
        except Exception as e:
            self.logger.warn('Found unexpected exception: '+type(e))
        finally:
            self._socket_mutex.release()
        return (False, b'')

    def on_change(self, callback):
        self._callbacks.append(callback)

    def __set_connected(self, state):
        if state != self.connected:
            for callback in self._callbacks:
                callback(self, state)
        if self.connected and not state:
            self.logger.warn(f'Socket {self.ip_addr}:{self.port} disconnected.')
        elif not self.connected and state:
            self.logger.log(f'Socket {self.ip_addr}:{self.port} connected.')
            self.on_connected.acquire()
            self.on_connected.notify_all()
            self.on_connected.release()
        self.connected = state
        if not self.connected and not self.reconnecting:
            self.reconnect_thread = Thread(
                target=self.__reconnect_thread, 
                args=(), daemon=True)
            self.reconnect_thread.start()

    def __reconnect_thread(self):
        self.reconnecting = True
        while not self.connected and not self.closed_by_user:
            try:
                self._socket_mutex.acquire()
                self._socket = socket(AF_INET, SOCK_STREAM)
                self._socket.settimeout(RECV_TIMEOUT)
                self._socket.connect((self.ip_addr, self.port))
                self.__set_connected(True)
                self.reconnecting = False
            except Exception as e:
                print('Could not connect:', e)
                self._socket_mutex.release()
                time.sleep(RECONNECT_TIME)
                self._socket_mutex.acquire()
            finally:
                self._socket_mutex.release()

if __name__ == '__main__':
    sock = StableSocket('127.0.0.1',6060)
    sock.send(b'I\'m here!')
    while True:
        res = sock.receive()
        print(res)
        time.sleep(2)
