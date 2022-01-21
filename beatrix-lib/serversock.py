from socket import socket, timeout, AF_INET, SOCK_STREAM, SO_REUSEPORT, SOL_SOCKET, SHUT_RDWR
from threading import Thread

BACKLOG_SIZE = 10

class ServerSocket():
    def __init__(self, port:int):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self._socket.bind(('', port))
        self._socket.settimeout(0.2)

        self._receive_callbacks = []
        self._receive_threads = []
        self._connections = []

        self.port = port

    def stop(self):
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

    def start(self):
        self.running = True
        self.conn_thread = Thread(target=self.__connection_thread, args=())   
        self.conn_thread.setDaemon(True)
        self.conn_thread.start()

    def send(self, data:bytes):
        for (conn, addr) in self._connections:
            try:
                conn.send(data)
            except BrokenPipeError:
                if (conn, addr) in self._connections:
                    self._connections.remove((conn, addr))
            except Exception as e:
                print(f'[!] Encountered unexpected exception while sending:\n', type(e), e)

    def recieve(self, callback:callable):
        self._receive_callbacks.append(callback)

    def __connection_thread(self):
        self._socket.listen(BACKLOG_SIZE)
        while self.running:
            try:
                conn, addr = self._socket.accept()
                print(f'[*] Opened connection from: {addr}')
                self._connections.append((conn, addr))
                thread = Thread(target=self.__recieve_thread, args=(conn, addr))
                thread.start() 
                self._receive_threads.append(thread)
            except timeout: pass
            except Exception as e:
                print('[!] Encountered unexpected exception while connecting:\n', type(e), e) 

    def __recieve_thread(self, conn, addr):
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
                    callback(data)
            except ConnectionResetError as e:
                conn_end()
            except Exception as e:
                print('[!] Encountered unexpected exception while receiving:\n', type(e), e) 
                


if __name__ == '__main__':
    import time
    socket = ServerSocket(6060)
    socket.start()
    socket.recieve(print)
    while True:
        print([x[1] for x in socket._connections])
        socket.send(b'hey!')
        time.sleep(2)
