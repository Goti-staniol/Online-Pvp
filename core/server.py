import socket 
import json


ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM


class Host:
    def __init__(self, ip: str = '0.0.0.0', port: int = 1313) -> None:
        self._ip = ip
        self._host = socket.socket(ADDRESS_FAMILY, SOCKET_TYPE)
        self._host_socket = None
        self.port = port

    @staticmethod
    def get_machine_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()

        return ip

    def run(self) -> None:
        self._host.bind((self._ip, self.port))
        self._host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._host.listen(1)
        
        self._host_socket, client_address = self._host.accept()
    
    def send(self, data: dict) -> None:
        # print('Отправлено:', data)
        self._host_socket.send(json.dumps(data).encode())
    
    def get_data(self, bufsize: int = 1024) -> dict | None:
        data = self._host_socket.recv(bufsize).decode()
        # print('Получено', data)
        return json.loads(data)


class Client:
    def __init__(self, ip: str = '0.0.0.0', port: int = 1313) -> None:
        self._ip = ip
        self._client_socket = None
        self.port = port
        
    def connect(self, ip: str, port: int) -> None:
        try:
            self._ip = ip
            self.port = port
            self._client_socket = socket.socket(ADDRESS_FAMILY, SOCKET_TYPE)
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
        self._client_socket.send(json.dumps(data).encode())

    def get_data(self, bufsize: int = 1024) -> dict | None:
        data = self._client_socket.recv(bufsize).decode()
        return json.loads(data)



