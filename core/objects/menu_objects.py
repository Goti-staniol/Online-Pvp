import json
import socket

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG, QTimer
from PyQt5 import uic

from core.decorators import run_is_thread
from core.game import run_game, host, client


class BaseWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._load_style()

    def _load_style(self) -> None:
        with open('core/styles/styles.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def move_to_window(self, window: QWidget):
        window.show()
        self.close()


class ConnectWindow(BaseWindow):
    ip_input: QLabel
    port_input: QLabel
    connect_btn: QPushButton
    back_btn: QPushButton

    def __init__(self, parent_window: QWidget) -> None:
        super().__init__()
        uic.loadUi('core/ui/connect_menu.ui', self)
        self._load_style()
        self.connect_btn.clicked.connect(lambda: self.connect_btn_handler())
        self.back_btn.clicked.connect(
            lambda: self.move_to_window(parent_window)
        )

    @run_is_thread
    def connect_btn_handler(self) -> None:
        ip = self.ip_input.text()
        port = int(self.port_input.text())

        client.connect(ip, port)
        QMetaObject.invokeMethod(self, 'hide', Qt.QueuedConnection)
        run_game('client')
        QMetaObject.invokeMethod(self, 'close', Qt.QueuedConnection)


class RunGameWindow(BaseWindow):
    console: QTextEdit

    def __init__(self):
        super().__init__()
        uic.loadUi('core/ui/run_game_menu.ui', self)
        self._load_style()
        self.index = 0
        self.timer = QTimer(self)
        self.server_thread = None

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.start_server()

    def _send_msg(self, msg: str) -> None:
        QMetaObject.invokeMethod(
            self.console,
            'append',
            Qt.QueuedConnection,
            Q_ARG(str, msg)
        )

    def _send_colored_msg(self, msg: str, color: str) -> None:
        color_msg = f"<span style='color:{color};'>{msg}</span>"
        self._send_msg(color_msg)

    @run_is_thread
    def start_server(self) -> None:
        with open('data/server_config.json', 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            try:
                if data['server']['ip'] == 'localdevice':
                    ip: str = host.get_machine_ip()
                    port: int = data['server']['port']
                    warning_msg: str = data['server']['warnings'].get(
                        'local_device_warning'
                    )
                    self._send_colored_msg(warning_msg, 'yellow')
                else:
                    ip: str = data['server']['ip']
                    port: int = data['server']['port']

                self._send_msg(f'Data to connect: \nIP - {ip}\nPORT - {port}')
                host.run(ip, port)
                QMetaObject.invokeMethod(self, 'hide', Qt.QueuedConnection)
                run_game('host')
                QMetaObject.invokeMethod(self, 'close', Qt.QueuedConnection)

            except (OSError, socket.gaierror):
                error_msg: str = data['server']['errors'].get(
                    'invalid_data'
                )
                self._send_colored_msg(f"{error_msg}", 'red')


class SettingsWindow(BaseWindow):
    ip_input: QLabel
    port_input: QLabel
    save_btn: QPushButton
    default_btn: QPushButton
    back_btn: QPushButton

    def __init__(self, parent_window: QWidget) -> None:
        super().__init__()
        uic.loadUi('core/ui/settings_menu.ui', self)
        self.parent_window = parent_window
        self._load_style()
        self.paste_data()
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.save_btn.clicked.connect(self.save_btn_handler)
        self.default_btn.clicked.connect(self.default_btn_handler)
        self.back_btn.clicked.connect(
            lambda: self.move_to_window(parent_window)
        )

    def save_btn_handler(self) -> None:
        with open('data/server_config.json', 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            data['server']['ip'] = self.ip_input.text()
            data['server']['port'] = int(self.port_input.text())

        with open('data/server_config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def default_btn_handler(self) -> None:
        self.ip_input.setText('localdevice')
        self.port_input.setText('1313')

        with open('data/server_config.json', 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            data['server']['ip'] = 'localdevice'
            data['server']['port'] = 1313

        with open('data/server_config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def paste_data(self) -> None:
        with open('data/server_config.json', 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            self.ip_input.setText(data['server']['ip'])
            self.port_input.setText(str(data['server']['port']))


class MainWindow(BaseWindow):
    run_game_btn: QPushButton
    connect_btn: QPushButton
    settings_btn: QPushButton

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('core/ui/main_menu.ui', self)
        self._load_style()
        self.run_game_window = RunGameWindow()
        self.settings_window = SettingsWindow(self)
        self.connect_window = ConnectWindow(self)
        self.run_game_btn.clicked.connect(self.open_run_game_window)
        self.settings_btn.clicked.connect(self.open_settings_window)
        self.connect_btn.clicked.connect(self.open_connect_window)

    def open_connect_window(self) -> None:
        self.connect_window.show()
        self.close()

    def open_settings_window(self) -> None:
        self.settings_window.show()
        self.close()

    def open_run_game_window(self) -> None:
        self.run_game_window.show()
        self.close()

# app = QApplication([])
# w = MainWindow()
# w.show()
# app.exec_()