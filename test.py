import socket

class Host:
    @staticmethod
    def get_machine_ip() -> str:
        """Возвращает IP-адрес машины, по которому можно подключаться в сети."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))  # Определяем IP исходящего соединения
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

print(Host.get_machine_ip())