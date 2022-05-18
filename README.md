# qgis-plugin-dev-tools

QGIS plugin development and packaging tools, which make managing runtime dependencies easy.

## Prerequisites

Your plugin package must be available to import from the python environment this tool is run in. For example, running `python -c "import your_plugin_package_name"` should not fail. Additionally, any dependency libraries must also be available in the python environment, so a dependency to `some_pypi_package` needs something like `pip install some_pypi_package` for this tool to work.

## Limitations

Bundling works by copying the code as-is and replacing the imports in all bundled files, so native library dependencies and other special cases might not work. To be safe, only depend on pure python libraries. Also verify the result zip works, since some import statements or `sys.modules` usage might not be supported.

## Setup

Install this library with `pip install qgis-plugin-dev-tools`.

Create a `pyproject.toml` tool section:

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
```

If the plugin runtime depends on external libraries, add the distribution names to `runtime_requires` list as abstract dependencies.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
runtime_requires = [
    "some_pypi_package"
]
```

## Plugin packaging

Run `qgis-plugin-dev-tools build` (short `qpdt b`) to package the plugin and any runtime dependencies to a standard QGIS plugin zip file, that can be installed and published.

By default config is read from `pyproject.toml`, changelog notes from `CHANGELOG.md`, version from latest changelog item title, and package is created in a `dist` directory in the current working directory. Changelog contents and version number are inserted to the `metadata.txt` file, so the version and changelog sections do not need manual updates.

## Plugin development mode

Run `qgis-plugin-dev-tools start` (short `qpdt s`) to launch QGIS with the plugin installed and ready for development.

By default config is read from `pyproject.toml` and runtime config from `.env` in the current working directory. Extra environment files can be passed using `-e` flag. `.env` must configure the executable path, and may configure debugger, profile name and any extra runtime variables necessary for the plugin.

```sh
QGIS_EXECUTABLE_PATH= # path to qgis-bin/qgis-bin-ltr or .exe equivalents, necessary
# DEBUGGER_LIBRARY= # debugpy/pydevd to start a debugger on init, library must be installed to the environment
# DEVELOPMENT_PROFILE_NAME= # name of the profile that qgis is launched with, otherwise uses default

# any other variables are added to the runtime QGIS environment
# SOMETHING=something
```

Development mode bootstraps the launched QGIS to have access to any packages available to the launching python environment, setups enviroment variables, configures a debugger, and installs and enables the developed plugin package.

Additionally editable installs for the plugin dependencies are supported. For example with a dependency to `some_pypi_package`, use `pip install -e /path/to/some_pypi_package` to provide `some_pypi_package` in editable mode from a local directory, and use [Plugin Reloader] to refresh new code when its changed on disk. This will also reload the declared dependencies.

## Development of qgis-plugin-dev-tools

See [development readme](./DEVELOPMENT.md).

## License & copyright

Licensed under GNU GPL v3.0.

Copyright (C) 2022 [National Land Survey of Finland].

[Plugin Reloader]: https://plugins.qgis.org/plugins/plugin_reloader
[National Land Survey of Finland]: https://www.maanmittauslaitos.fi/en
