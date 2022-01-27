from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_SNDBUF, SOL_SOCKET, SHUT_RDWR, timeout
from threading import Thread, Condition, Lock
import time

SEND_TIMEOUT = 0.8
RECV_TIMEOUT = 0.6
RECONNECT_TIME = 0.5
VIDEO_PORT = 37020

class ClientSocket():
    def __init__(self, ip_addr:str, port:int, logger=None):
        self.ip_addr = ip_addr
        self.port    = port
        
        self.reconnecting = False
        self.connected    = False
        self._on_connected = Condition()
        
        self._socket_mutex = Lock()
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(RECV_TIMEOUT)

        self.closed_by_user = False
        self._callbacks = []

        self.logger = logger
        if logger == None:
            try: from lib.logger import Logger
            except: from logger import Logger
            self.logger = Logger()

    def start(self):
        """ Opens the socket and enables automatic reconnection. """
        self.reconnect_thread = Thread(
            target=self.__reconnect_thread, 
            args=(), daemon=True)
        self.reconnect_thread.start()

    def is_connected(self) -> bool:
        """ Checks if the given socket is currently connected. """
        return not self.closed_by_user and self.connected

    def stop(self):
        """ Closes the socket and stops any automatic reconnection attempts.  """
        self.closed_by_user = True
        self._socket_mutex.acquire()
        try: self._socket.shutdown(SHUT_RDWR)
        except: pass
        self._socket.close()
        self._socket_mutex.release()
        if self.reconnect_thread:
            self.reconnect_thread.join()

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
                self._on_connected.acquire()
                self._on_connected.wait(timeout=SEND_TIMEOUT)
                self._on_connected.release()
            if self.connected:
                self._socket_mutex.acquire()
                self._socket.sendall(data)
                return True
        except BrokenPipeError:
            self.__set_connected(False)
        except Exception as e:
            self.logger.exception(e, 'ClientSocket.send')
        finally:
            if self._socket_mutex.locked():
                self._socket_mutex.release()
        return False

    def receive(self, buffer_size=1024) -> (bool, bytes):
        """ Tries to receive a buffer of 1024 bytes or a given size worth of data. If any data is 
        received it will return it in a tuple prepended with `True`, if it fails to receive data; 
        either through an error or timeout it will return `False` and an empty byte array.

        Arguments:
            buffer_size (int): The maximum amount of bytes to receive (defaults to 1024).

        Returns:
            (True, data) when data was successfully sent and (False, '') when not.
        """
        try:
            self._socket_mutex.acquire()
            data = self._socket.recv(buffer_size)
            if len(data) == 0:
                raise ConnectionResetError()
            else:
                return (True, data)
        except timeout:
            return (False, b'')
        except ConnectionResetError as e:
            self.__set_connected(False)
        except OSError as e:
            self.__set_connected(False)
        except Exception as e:
            self.logger.exception(e, 'ClientSocket.receive')
        finally:
            self._socket_mutex.release()
        return (False, b'')

    def on_change(self, callback:callable):
        """ Adds a callback function to the socket that will be called whenever the connection state of 
        the socket changes. """
        self._callbacks.append(callback)

    def __set_connected(self, state:bool):
        """ Updates the `self.connected` parameter and does all of the necessary bookkeeping like 
        starting the auto reconnect thread and calling any registered callbacks. """
        inform_callbacks = (state != self.connected)
        if self.connected and not state:
            self.logger.warn(f'Socket {self.ip_addr}:{self.port} disconnected.')
        elif not self.connected and state:
            self.logger.log(f'Socket {self.ip_addr}:{self.port} connected.')
            self._on_connected.acquire()
            self._on_connected.notify_all()
            self._on_connected.release()
        self.connected = state
        if inform_callbacks:
            for callback in self._callbacks:
                    callback(self, state)
        if not self.connected and not self.reconnecting:
            self.reconnect_thread = Thread(
                target=self.__reconnect_thread, 
                args=(), daemon=True)
            self.reconnect_thread.start()

    def __reconnect_thread(self):
        """ Automatically reconnects the socket when the connection is lost. """
        self.reconnecting = True
        while not self.connected and not self.closed_by_user:
            try:
                self._socket_mutex.acquire()
                self._socket = socket(AF_INET, SOCK_STREAM)
                self._socket.settimeout(RECV_TIMEOUT)
                self._socket.connect((self.ip_addr, self.port))
                self.__set_connected(True)
                self.reconnecting = False
            except timeout:
                self._socket_mutex.release()
                time.sleep(RECONNECT_TIME)
                self._socket_mutex.acquire()
            except ConnectionRefusedError:
                self._socket_mutex.release()
                time.sleep(RECONNECT_TIME)
                self._socket_mutex.acquire()
            except Exception as e:
                self.logger.exception(e, 'ClientSocket.__reconnect_thread')
                self._socket_mutex.release()
                time.sleep(RECONNECT_TIME)
                self._socket_mutex.acquire()
            finally:
                self._socket_mutex.release()
