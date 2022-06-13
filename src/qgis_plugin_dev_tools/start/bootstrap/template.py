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

import atexit
import contextlib
import functools
import os
import pickle
import sys
from dataclasses import asdict, dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Dict, List, Optional

# defer qgis.* imports until necessary to avoid loading those
# for the interpreter that launches the bootstrapping, since it
# will import the config class from this module


def _unload_package_modules(package_names: List[str]) -> None:
    to_clean_names = [
        module_name
        for module_name in sys.modules
        if any(
            module_name == package_name or module_name.startswith(f"{package_name}.")
            for package_name in package_names
        )
    ]
    for module_name in to_clean_names:
        try:  # noqa SIM105
            if hasattr(sys.modules[module_name], "qCleanupResources"):
                sys.modules[module_name].qCleanupResources()
        except Exception:  # noqa PIE786
            pass
        try:  # noqa SIM105
            del sys.modules[module_name]
        except Exception:  # noqa PIE786
            pass


def _monkeypatch_plugin_module_unload_to_unload_dependencies(
    plugin_package_name: str, plugin_dependency_package_names: List[str]
) -> None:
    from qgis.core import Qgis, QgsMessageLog

    if len(plugin_dependency_package_names) > 0:
        QgsMessageLog.logMessage(
            f"patching plugin {plugin_package_name} unload "
            f"to unload dependencies {plugin_dependency_package_names} also",
            "Bootstrap",
            level=Qgis.Info,
        )

        from qgis.utils import (  # noqa N813 (qgis naming)
            _unloadPluginModules as _original_unload,
        )

        unload_plugin_dependency_modules = functools.partial(
            _unload_package_modules, plugin_dependency_package_names
        )

        def _custom_unload(packageName: str) -> bool:  # noqa N803 (qgis naming)
            original_return = _original_unload(packageName)
            if packageName == plugin_package_name:
                unload_plugin_dependency_modules()
            return original_return

        import qgis.utils as qgis_utils_module

        qgis_utils_module._unloadPluginModules = _custom_unload


def _monkeypatch_plugin_reload_to_reload_extra_plugins(
    main_plugin_package_name: str, extra_plugin_package_names: List[str]
) -> None:
    from qgis.core import Qgis, QgsMessageLog
    from qgis.utils import loadPlugin as _original_load  # noqa N813 (qgis naming)
    from qgis.utils import startPlugin
    from qgis.utils import unloadPlugin as _original_unload  # noqa N813 (qgis naming)

    def _custom_unload(packageName: str) -> bool:  # noqa N803 (qgis naming)
        original_return = _original_unload(packageName)

        if packageName == main_plugin_package_name:
            for plugin_package_name in extra_plugin_package_names:
                with contextlib.suppress(Exception):
                    _original_unload(plugin_package_name)

        return original_return

    def _custom_load(packageName: str) -> bool:  # noqa N803 (qgis naming)
        if packageName == main_plugin_package_name:
            for plugin_package_name in extra_plugin_package_names:
                with contextlib.suppress(Exception):
                    _original_load(plugin_package_name)
                    startPlugin(plugin_package_name)
                    QgsMessageLog.logMessage(
                        f"activating {plugin_package_name} plugin",
                        "Bootstrap",
                        level=Qgis.Info,
                    )

        return _original_load(packageName)

    import qgis.utils as qgis_utils_module

    qgis_utils_module.unloadPlugin = _custom_unload
    qgis_utils_module.loadPlugin = _custom_load


def _setup_runtime_library_paths(runtime_library_paths: List[Path]) -> None:
    from qgis.core import Qgis, QgsMessageLog

    QgsMessageLog.logMessage(
        "setting dev env package paths", "Bootstrap", level=Qgis.Info
    )
    sys.path.extend(str(p) for p in runtime_library_paths)


def _setup_runtime_environment(runtime_environment: Dict[str, str]) -> None:
    from qgis.core import Qgis, QgsMessageLog

    QgsMessageLog.logMessage("setting dev env variables", "Bootstrap", level=Qgis.Info)
    os.environ.update(runtime_environment)


def _enable_extra_plugins(
    main_plugin_package_name: str, extra_plugin_package_names: List[str]
) -> None:
    from qgis.PyQt.QtCore import QSettings
    from qgis.utils import plugin_paths, unloadPlugin

    for plugin_package_name in extra_plugin_package_names:
        spec = find_spec(plugin_package_name)
        if spec is not None and spec.origin is not None:
            parent_path = Path(spec.origin).parent.parent
            plugin_paths.append(str(parent_path))
            unloadPlugin(plugin_package_name)
            QSettings().setValue(f"PythonPlugins/{plugin_package_name}", "true")

    _monkeypatch_plugin_reload_to_reload_extra_plugins(
        main_plugin_package_name, extra_plugin_package_names
    )


def _enable_plugin(
    plugin_package_name: str,
    plugin_package_path: Path,
    plugin_dependency_package_names: List[str],
) -> None:
    from pyplugin_installer.installer_data import plugins as installer_plugins
    from qgis.core import Qgis, QgsMessageLog
    from qgis.PyQt.QtCore import QSettings
    from qgis.utils import (
        loadPlugin,
        plugin_paths,
        reloadPlugin,
        startPlugin,
        unloadPlugin,
        updateAvailablePlugins,
    )

    # if plugin dialog info is not necessary, its possible to just inject the data
    # here as a configparser instance to qgis.utils.plugins_metadata_parser
    # and only generate metadata when building the actual plugin zip file?
    # config = ConfigParser()
    # config.read_dict(
    #     {
    #         "general": {
    #             "name": "My plugin",
    #             "qgisMinimumVersion": "3.10",
    #             "qgisMaximumVersion": "3.99",
    #             "description": "My plugin",
    #             # 'about': '',
    #             "version": "0.0.0",
    #             "author": "example",
    #             "email": "example@example.org",
    #             # 'changelog': '',
    #             "experimental": "True",
    #             "deprecated": "False",
    #             # 'tags': '',
    #             # 'homepage': '',
    #             # 'repository': '',
    #             # 'tracker': '',
    #             # 'icon': '',
    #             # 'category': '',
    #         },
    #     }
    # )
    # plugins_metadata_parser["my_plugin"] = config

    QgsMessageLog.logMessage(
        f"activating {plugin_package_name} plugin",
        "Bootstrap",
        level=Qgis.Info,
    )

    _monkeypatch_plugin_module_unload_to_unload_dependencies(
        plugin_package_name, plugin_dependency_package_names
    )

    plugin_paths.append(str(plugin_package_path.parent))
    updateAvailablePlugins()
    unloadPlugin(plugin_package_name)
    loadPlugin(plugin_package_name)
    startPlugin(plugin_package_name)
    QSettings().setValue(f"PythonPlugins/{plugin_package_name}", "true")
    installer_plugins.getAllInstalled()

    QgsMessageLog.logMessage(
        f"activated {plugin_package_name} plugin",
        "Bootstrap",
        level=Qgis.Info,
    )

    # Make sure Plugin Reloader plugin (3rd party plugin for QGIS plugin development)
    # will use monkeypatched load and unload functions.
    # https://github.com/borysiasty/plugin_reloader
    reloadPlugin("plugin_reloader")


def _start_debugger(library_name: Optional[str], python_executable_path: Path) -> None:
    from qgis.core import Qgis, QgsMessageLog

    try:
        if library_name == "debugpy":
            import debugpy  # noqa SC200

            # at least on windows qgis resets the env and sys.executable points
            # to the qgis executable, hold on to the original python to use here
            debugpy.configure(python=str(python_executable_path))  # noqa SC200
            debugpy.listen(("localhost", 5678))  # noqa SC200

        elif library_name == "pydevd":
            import pydevd  # noqa SC200

            pydevd.settrace(  # noqa SC200
                "localhost", port=5678, stdoutToServer=True, stderrToServer=True
            )

        else:
            return

    except Exception as e:  # noqa PIE786
        QgsMessageLog.logMessage(
            f"failed to start {library_name} debugger: {e}",
            "Bootstrap",
            level=Qgis.Info,
        )
    else:
        QgsMessageLog.logMessage(
            f"started {library_name} debugger",
            "Bootstrap",
            level=Qgis.Info,
        )


@dataclass
class BootstrapConfig:
    daemon_socket_port: int
    runtime_library_paths: List[Path]
    runtime_environment: Dict[str, str]
    plugin_package_path: Path
    plugin_package_name: str
    plugin_dependency_package_names: List[str]
    debugger_library: Optional[str]
    bootstrap_python_executable_path: Path
    extra_plugin_package_names: List[str]

    def __str__(self) -> str:
        result = ""
        for k, v in asdict(self).items():
            if isinstance(v, list):
                result += f"  {k}=\n    " + "\n    ".join(map(str, v)) + "\n"
            else:
                result += f"  {k}={v}\n"
        return result


def _do_bootstrap(config: BootstrapConfig) -> None:
    from qgis.core import Qgis, QgsMessageLog
    from qgis.PyQt.QtNetwork import QAbstractSocket, QHostAddress, QTcpSocket
    from qgis.utils import iface

    QgsMessageLog.logMessage("bootstrap called", "Bootstrap", level=Qgis.Info)

    _socket = QTcpSocket()
    atexit.register(_socket.abort)

    def _on_socket_connected() -> None:
        _socket.abort()
        _socket.connected.disconnect()
        _socket.errorOccurred.disconnect()
        QgsMessageLog.logMessage("connected to daemon", "Bootstrap", level=Qgis.Info)

        _setup_runtime_library_paths(config.runtime_library_paths)
        _setup_runtime_environment(config.runtime_environment)
        _enable_extra_plugins(
            config.plugin_package_name, config.extra_plugin_package_names
        )
        _enable_plugin(
            config.plugin_package_name,
            config.plugin_package_path,
            config.plugin_dependency_package_names,
        )
        _start_debugger(
            config.debugger_library, config.bootstrap_python_executable_path
        )

    def _on_socket_error(error_type: QAbstractSocket.SocketError) -> None:
        _socket.abort()
        _socket.connected.disconnect()
        _socket.errorOccurred.disconnect()
        if error_type == QAbstractSocket.SocketError.RemoteHostClosedError:
            QgsMessageLog.logMessage("daemon was closed", "Bootstrap", level=Qgis.Info)
        else:
            QgsMessageLog.logMessage(
                "connection to daemon failed", "Bootstrap", level=Qgis.Warning
            )

    def _on_qgis_initialized() -> None:
        QgsMessageLog.logMessage("qgis initialized", "Bootstrap", level=Qgis.Info)
        _socket.connectToHost(
            QHostAddress.SpecialAddress.LocalHost, config.daemon_socket_port
        )
        QgsMessageLog.logMessage("connecting to daemon", "Bootstrap", level=Qgis.Info)

    _socket.connected.connect(_on_socket_connected)
    _socket.errorOccurred.connect(_on_socket_error)
    iface.initializationCompleted.connect(_on_qgis_initialized)


if __name__ == "__main__":
    # when running this code from qgis startup --code file
    # the config is templated here as a pickled dataclass
    _do_bootstrap(BootstrapConfig(**pickle.loads(b"$DATACLASS_AS_PICKLED_DICT$")))
