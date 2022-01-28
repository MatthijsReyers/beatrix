from socket import socket, timeout, AF_INET, SOCK_STREAM, SO_REUSEPORT, SOL_SOCKET, SHUT_RDWR, SO_SNDBUF
from threading import Thread
import struct

BACKLOG_SIZE = 10

class ServerSocket():
    def __init__(self, port:int, buffer_size:int=None):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        if buffer_size != None:
            self._socket.setsockopt(SOL_SOCKET, SO_SNDBUF, buffer_size)
        self._socket.bind(('', port))
        self._socket.settimeout(0.2)

        self._receive_callbacks = []
        self._receive_threads = []
        self._connections = []

        self.port = port
        self.running = False

    def start(self):
        """ Makes the socket listen for incoming connections on the provided port, this happens on a 
        separate thread so the start function is not blocking. """
        self.running = True
        self.conn_thread = Thread(target=self.__connection_thread, args=())   
        self.conn_thread.setDaemon(True)
        self.conn_thread.start()

    def stop(self):
        """ Stops the socket from listening on the provided port and gracefully closes all currently 
        active network connections and running threads. """
        self.running = False
        for (conn, _) in self._connections:
            conn.close()
        self._socket.shutdown(SHUT_RDWR)
        self._socket.close()
        if self.conn_thread and self.conn_thread.is_alive():
            self.conn_thread.join()
        for thread in self._receive_threads:
            if thread.is_alive():
                thread.join()

    def send(self, data:bytes, ip:str=None):
        """ Tries to send the given data to either all connected clients or the one with the given IP 
        address, note that this happens on the calling thread and will block until all connections have 
        either received the data or timed out. 
        
        Arguments:
            data (bytes): Data to send, should be a bytestring but regular strings will be automatically
                converted to bytestrings.
            ip (str): Optional Ip address to send to, all clients will receive data if none is provided.
        """
        for (conn, addr) in self._connections:
            try:
                if ip == None or addr[1] == ip:
                    conn.send(data)
            except BrokenPipeError:
                if (conn, addr) in self._connections:
                    self._connections.remove((conn, addr))
            except Exception as e:
                print(f'[!] Encountered unexpected exception while sending:\n', type(e), e)
                self._connections.remove((conn, addr))
                
    def on_receive(self, callback:callable):
        """ Adds a callback function to the socket that will be called whenever one of the clients sends
        something to this server socket. 
        
        Arguments:
            callback: Function/callable with parameters (data:bytes, client:(ip,port)).
        """
        self._receive_callbacks.append(callback)

    def __connection_thread(self):
        self._socket.listen(BACKLOG_SIZE)
        while self.running:
            try:
                conn, addr = self._socket.accept()
                print(f'[*] Opened connection from: {addr}')
                self._connections.append((conn, addr))
                thread = Thread(target=self.__receive_thread, args=(conn, addr))
                thread.start() 
                self._receive_threads.append(thread)
            except timeout: 
                pass
            except OSError as e:
                if not self.running: 
                    break
                else:
                    print('[!] Encountered unexpected exception while connecting:\n', type(e), e) 
            except Exception as e:
                print('[!] Encountered unexpected exception while connecting:\n', type(e), e) 

    def __receive_thread(self, conn, addr):
        def conn_end():
            if (conn, addr) in self._connections:
                conn.close()
                print('[!] Closed connection from: ',addr)
                self._connections.remove((conn, addr))
        while self.running:
            try: 
                data = conn.recv(1024)
                if len(data) == 0: 
                    conn_end()
                    break
                for callback in self._receive_callbacks:
                    callback(data, addr)
            except ConnectionResetError: conn_end()
            except OSError: conn_end()
            except Exception as e:
                print('[!] Encountered unexpected exception while receiving:\n', type(e), e) 
                print(data)
                conn_end()