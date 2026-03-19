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

If the plugin runtime dependencies have many dependencies themselves, it is possible to include those recursively with `auto_add_recursive_runtime_dependencies`. Alternatively, all the requirements can be listed in `runtime_requires`.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
runtime_requires = [
    "some_pypi_package"
]
auto_add_recursive_runtime_dependencies = true
```

If the plugin runtime dependencies do not work with the aforementioned configuration, the dependencies can be added to the Python Path with `use_dangerous_vendor_sys_path_append` flag. This method might be **unsafe** if there are conflicts between dependency versions of different plugins.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
runtime_requires = [
    "some_pypi_package_with_binary_files"
]
use_dangerous_vendor_sys_path_append = true
```

By default build version number is read from changelog top-most second level heading having format `## version anything`. This behaviour is configurable with `version_number_source` to use plugin package distribution metadata. Optionally, the version number can also be provided as an argument for the build script using `qpdt b --version 0.1.0-rc2`.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
version_number_source = "distribution"  # or "changelog" (default if missing)
```

Changelog path can be configured with `changelog_file_path` option. By default it is assumed to be `CHANGELOG.md` in the same directory as `pyproject.toml`.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
changelog_file_path = "../../CHANGELOG.md"
```

QGIS plugins are required to have a LICENSE file included in the plugin package. However, usually it is more convenient to keep the license file in the root of the repository. LICENSE can be copied automatically to the plugin zip while packaging if such file is found. A relative path to the license file can also be configured with `license_file_path` option.

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
license_file_path = "docs/my-license.md"
```

## Plugin packaging

Run `qgis-plugin-dev-tools build` (short `qpdt b`) to package the plugin and any runtime dependencies to a standard QGIS plugin zip file, that can be installed and published.

By default config is read from `pyproject.toml`, changelog notes from `CHANGELOG.md`, version from changelog, and package is created in a `dist` directory in the current working directory. Changelog contents and version number are inserted to the `metadata.txt` file, so the version and changelog sections do not need manual updates.

## Plugin publishing

Run `qgis-plugin-dev-tools publish <file>` (short `qpdt publish <file>`) to publish a previously built plugin zip file to QGIS plugin repository.

By default username and password are read from `QPDT_PUBLISH_USERNAME` and `QPDT_PUBLISH_PASSWORD` environment variables.

## Updating translations

Run `qgis-plugin-dev-tools transup` (short `qpdt ts`) to creat or update ts files for translating the plugin. This command can be configured with:

```toml
[tool.qgis_plugin_dev_tools]
translation_language_codes = [
    "fi",
]
translation_search_paths = [
    "src/your_plugin_package_name"
]
translation_destination_path = "src/your_plugin_package_name/resources/i18n"
# translation_pylupdate_command = "/usr/bin/pylupdate6" # Override of pylupdate5 command
```

By default, on Windows translation uses python script `PyQt5.pylupdate_main` and on other platforms `pylupdate5` or `pylupdate6` executable.

### Updating translations only when there are changes

If you want to update translation files only if there are new strings to be translated, you can use `qpdt transup --check-changes` (short `qpdt ts --check-changes`).
This flag omits all the line number and refactoring changes in the translation files, since it won't affect how translations work.
This is useful if used together with tools like `pre-commit`.

## Compiling translations

Run `qgis-plugin-dev-tools transcompile` (short `qpdt tc`) to compile ts files into qm files that can be used the plugin.
This command reads the same configuration as `transup` command.

> [!WARNING]
> Usually "lrelease" binary does not ship on Windows when installing QGIS. In that case use Qt-linguiest (linguist.exe) to compile translations.

## Plugin development mode

Run `qgis-plugin-dev-tools start` (short `qpdt s`) to launch QGIS with the plugin installed and ready for development.

By default config is read from `pyproject.toml` and runtime config from `.env` in the current working directory. Extra environment files can be passed using `-e` flag. `.env` must configure the executable path, and may configure debugger, profile name and any extra runtime variables necessary for the plugin.

```sh
QGIS_EXECUTABLE_PATH= # path to qgis-bin/qgis-bin-ltr or .exe equivalents, necessary
# DEBUGGER_LIBRARY= # debugpy/pydevd to start a debugger on init, library must be installed to the environment
# DEVELOPMENT_PROFILE_NAME= # name of the profile that qgis is launched with, otherwise uses default
# QGIS_LOCALE= # locale code of QGIS, otherwise uses default
# QGIS_GUI_INI= # path to ini file containing QGIS UI customizations

# any other variables are added to the runtime QGIS environment
# SOMETHING=something
```

`.env` can also be configured with `pyproject.toml` configuration `env_file_path` option..

```toml
[tool.qgis_plugin_dev_tools]
plugin_package_name = "your_plugin_package_name"
env_file_path = "../../.env"
```

Development mode bootstraps the launched QGIS to have access to any packages available to the launching python environment, setups enviroment variables, configures a debugger, and installs and enables the developed plugin package.

Additionally editable installs for the plugin dependencies are supported. For example with a dependency to `some_pypi_package`, use `pip install -e /path/to/some_pypi_package` to provide `some_pypi_package` in editable mode from a local directory, and use [Plugin Reloader] to refresh new code when its changed on disk. This will also reload the declared dependencies.

### Developing multiple plugins

Development mode also enables using and developing multiple plugins easily if certain requirements are satisfied for all extra plugins:

* Extra plugin must be installable python packages
  * See e.g. [Quickstart for setuptools]
* Extra plugin must have entry point in group "qgis_plugin_dev_tools"
  * See for example: [Entry point usage with setuptools]
  * Use plugin package name for entry point name
* Extra plugin needs to be installed in the same python environment where this tool is run in

Extra plugins are loaded on launch and reloaded together with the main plugin if [Plugin Reloader] is used.

You can disable plugin auto-load by using `pyproject.toml` configuration (for example when using a dependency, that also provides a plugin entrypoint):

```toml
[tool.qgis_plugin_dev_tools]
disabled_extra_plugins = [
  "unwanted_plugin_package_name",
]
```

## Use with pre-commit

Some of the qgis-plugin-dev-tools commands are exposed as pre-commit hooks to be run with tools like pre-commit and prek.
workflow, add something like the below to the `repos` list in the project's `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/nlsfi/qgis-plugin-dev-tools
  rev: v0.11.0
  hooks:
  - id: update-translations # runs "qgis-plugin-dev-tools transup" command
    # language: system # on Windows you might want to set this to access PyQt5.pylupdate_main
    # args: ["--pyproject-toml", "path/to/pyproject.toml"] # optionally give path to pyproject.toml
    # The flag --check-changes flag is used, to leave it out, set args: []

```

### Normalize XML files

This repository provides a hook for normalizing XML files. By default, the hook is applied to `.xml`, `.qml`, and `.ui` files; note that QML files may contain non-valid XML. In addition to formatting, the hook supports removing specific tags from the xml using the `--remove-tag` argument. Example usage:

```yaml
- repo: https://github.com/nlsfi/qgis-plugin-dev-tools
  rev: v0.12.0
  hooks:
    - id: normalize-xml
      args: [
        "--remove-tag", "fieldConfiguration"
      ]
```

## Development of qgis-plugin-dev-tools

See [development readme](./DEVELOPMENT.md).

## License & copyright

Licensed under GNU GPL v3.0.

Copyright (C) 2022-2026 [National Land Survey of Finland].

[Plugin Reloader]: https://plugins.qgis.org/plugins/plugin_reloader
[National Land Survey of Finland]: https://www.maanmittauslaitos.fi/en
[Quickstart for setuptools]: https://setuptools.pypa.io/en/latest/userguide/quickstart.html
[Entry point usage with setuptools]: https://setuptools.pypa.io/en/latest/userguide/entry_point.html#advertising-behavior
