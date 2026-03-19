#  Copyright (C) 2026 National Land Survey of Finland
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

# json rpc api spec in https://plugins.qgis.org/plugins/RPC2/

import logging
import os
from base64 import b64encode
from pathlib import Path
from typing import cast
from uuid import uuid4

import requests

LOGGER = logging.getLogger(__name__)

HTTP_STATUS_CODE_OK = 200


def publish_plugin_zip_file(plugin_zip_file_path: Path) -> None:
    username = os.environ.get("QPDT_PUBLISH_USERNAME")
    password = os.environ.get("QPDT_PUBLISH_PASSWORD")

    if not username or not password:
        raise ValueError(
            "credentials in QPDT_PUBLISH_* variables are not configured properly"
        )

    if not plugin_zip_file_path.exists():
        raise FileNotFoundError(
            f"could not find plugin zip file in {plugin_zip_file_path.resolve()}"
        )

    zip_binary_contents = plugin_zip_file_path.read_bytes()
    request_identifier = f"qgis-plugin-dev-tools-{uuid4()}"
    body = {
        "jsonrpc": "2.0",
        "method": "plugin.upload",
        "params": [b64encode(zip_binary_contents).decode("utf-8")],
        "id": request_identifier,
    }

    LOGGER.debug(
        "sending POST request to plugin RPC api with body %s",
        (body | {"params": ["<base64 zip contents>"]}),
    )

    response = requests.post(
        url="https://plugins.qgis.org/plugins/RPC2/",
        json=body,
        auth=(username, password),
    )

    LOGGER.debug(
        "got response from plugin RPC api with body %s",
        response.text,
    )

    if response.status_code != HTTP_STATUS_CODE_OK:
        raise Exception(
            "QGIS plugin repository plugin upload "
            f"HTTP request failed with status {response.status_code}"
        )
    if "error" in response.json():
        raise Exception(
            "QGIS plugin repository plugin upload "
            f"request returned error response {response.json().get('error')}"
        )

    plugin_id, version_id = cast("dict[str, tuple[int, int]]", response.json()).get(
        "result", (None, None)
    )

    LOGGER.info("uploaded plugin id %s & version id %s", plugin_id, version_id)
