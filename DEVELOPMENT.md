# qgis-plugin-dev-tools development

## Development environment setup

- Create a venv: `python -m venv .venv`
  - Having access to QGIS packages with suitable executable and `--system-site-packages` flag is not strictly necessary for now, since QGIS imports are deferred and those functions are not tested
- Install requirements: `pip install -r requirements.txt --no-deps --only-binary=:all:`
  - `pip-sync requirements.txt` can be used if `pip-tools` is installed
- Run tests: `pytest`

## Requirements changes

This project uses `pip-tools`. To update requirements, do `pip install pip-tools`, change `requirements.in` and use `pip-compile requirements.in` to generate new `requirements.txt` with fixed versions.

## Code style

Included `.code-workspace` has necessary options set (linting, formatting, tests) set for VS Code.

Verify code style with `pre-commit run --all-files`, or use `pre-commit install` to generate an actual git hook.

## Release steps

- Set version number to the main branch
  - Update version in `__init__.py`
  - Add the version number and a release date to the unreleased section in the changelog, and link the version number to a tag url (for the tag created in next step)
- Create a release from the main branch
  - Create a `vX.X.X` style tag
  - Create a release
  - Action should trigger from the release and build and publish the package to PyPI
- Set new development version number to the main branch
  - Update version tag in `__init__.py` to be the next version with a `.devX` suffix
  - Add new unreleased section to the changelog
