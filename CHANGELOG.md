# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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
