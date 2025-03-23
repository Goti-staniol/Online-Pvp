import socket 
import json
import threading


ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM


class Host:
    def __init__(self) -> None:
        self._ip: str = ''
        self.port: int = 0
        self._host = socket.socket(ADDRESS_FAMILY, SOCKET_TYPE)
        self._host_socket = None
        self._lock = threading.Lock()

    @staticmethod
    def get_machine_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip: str = s.getsockname()[0]
        s.close()

        return ip
    
    def run(self, ip: str, port: int) -> None:
        self._ip = ip
        self.port = port
        self._host.bind((self._ip, self.port))
        self._host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._host.listen(1)
        
        self._host_socket, client_address = self._host.accept()
    
    def send(self, data: dict) -> None:
        with self._lock:
            # print('Отправлено:', data)
            self._host_socket.send(json.dumps(data).encode())

    
    def get_data(self, bufsize: int = 1024) -> dict | None:
        with self._lock:
            data = self._host_socket.recv(bufsize).decode()
            return json.loads(data)


class Client:
    def __init__(self) -> None:
        self._ip: str = ''
        self.port: int = 0
        self._client_socket = socket.socket(ADDRESS_FAMILY, SOCKET_TYPE)
        self._lock = threading.Lock()
        
    def connect(self, ip: str, port: int) -> None:
        try:
            self._ip = ip
            self.port = port
            self._client_socket.connect((self._ip, self.port))
        except ConnectionRefusedError:
            raise ValueError(
                f'Connection refused on IP: {self._ip}, Port: {self.port}'
            )
        except socket.gaierror:
            raise ValueError(
                f'Invalid IP address or hostname: {self._ip}.'
            )

    def send(self, data: dict) -> None:
        with self._lock:
            self._client_socket.send(json.dumps(data).encode())

    def get_data(self, bufsize: int = 1024) -> dict | None:
        with self._lock:
            data = self._client_socket.recv(bufsize).decode()
            return json.loads(data)

