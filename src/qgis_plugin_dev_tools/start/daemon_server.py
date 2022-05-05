#  Copyright (C) 2022 National Land Survey of Finland
#  (https://www.maanmittauslaitos.fi/en).
#
#
#  This file is part of qgis-plugin-dev-tools.
#
#  qgis-plugin-dev-tools is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  qgis-plugin-dev-tools is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with qgis-plugin-dev-tools. If not, see <https://www.gnu.org/licenses/>.

from contextlib import contextmanager
from socketserver import BaseRequestHandler, TCPServer
from typing import Callable, Generator, Tuple

DAEMON_SERVER_TIMEOUT = 60


class SingleRequestHandlingTCPServer(TCPServer):
    timeout = DAEMON_SERVER_TIMEOUT
    is_timeout = False

    def handle_timeout(self) -> None:
        self.is_timeout = True
        return super().handle_timeout()


@contextmanager
def start_daemon_server() -> Generator[Tuple[int, Callable[[], bool]], None, None]:
    # TODO: add hot reload instead of closing the daemon?
    # watcher = QFileSystemWatcher([str(p) for p in Path(plugin_path).rglob('*.py')])
    # watcher.fileChanged.connect(send_something_to_socket)

    with SingleRequestHandlingTCPServer(("localhost", 0), BaseRequestHandler) as server:
        _, port = server.server_address

        def _handle_single_request_callback() -> bool:
            server.handle_request()
            return server.is_timeout

        yield port, _handle_single_request_callback
