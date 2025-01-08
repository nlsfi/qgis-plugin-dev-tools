# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.1] - 2025-01-08

- Fix: Fix license copying

## [0.9.0] - 2025-01-08

- Feat: Copy license into the plugin zip while deploying

## [0.8.0] - 2024-08-23

- Feat: Add locale and ui ini options to be able to further customize development environment

## [0.7.0] - 2024-05-21

- Fix: Bundle contents by parsing pep-compliant distribution file catalog instead of possibly missing tool-specific top-level.txt
- Feat: Allow disabling auto-loaded entrypoint plugins

## [0.6.2] - 2023-09-27

- Fix: Fix issues with bundling requirements of the requirements recursively

## [0.6.1] - 2023-09-06

- update author email

## [0.6.0] - 2023-02-17

- Feat: Support dependencies having package references in .ui files

## [0.5.0] - 2022-11-09

- Feat: Add publish command to cli
- Fix: Support build without actually importing the code
- Fix: Preserve case for key names in metadata file

## [0.4.0] - 2022-11-01

- Feat: Add an option to get version from distribution metadata
- Fix: Rewrite imports correctly when dependency name is a prefix of the plugin package name

## [0.3.0] - 2022-09-02

- Feat: Add an option to append vendor package to the Python Path
- Feat: Add an option to bundle requirements of the requirements recursively
- Feat: Add module packages and .pyd files to the bundle if found
- Feat: Add version as an optional build argument
- Chore: Drop support from Python < 3.9

## [0.2.1] - 2022-07-07

- Fix: Correct some plain import rewrites

## [0.2.0] - 2022-06-13

- Feat: enable extra plugins in development mode

## [0.1.2] - 2022-05-30

- Fix: use UTF-8 encoding for file reads/writes

## [0.1.1] - 2022-05-16

- Fix: rewrite runtime requirement imports correctly

## [0.1.0] - 2022-05-12

- Initial release: `start` and `build` commands with minimal configuration options.

[0.1.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.1.0
[0.1.1]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.1.1
[0.1.2]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.1.2
[0.2.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.2.0
[0.2.1]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.2.1
[0.3.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.3.0
[0.4.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.4.0
[0.5.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.5.0
[0.6.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.6.0
[0.6.1]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.6.1
[0.6.2]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.6.2
[0.7.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.7.0
[0.8.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.8.0
[0.9.0]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.9.0
[0.9.1]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v0.9.1
