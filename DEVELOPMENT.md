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

- Make a commit with the release version number in the files
  - Update version tag in `__init__.py` with the release version number (remove `.post0` suffix and update accordingly)
  - Replace the unreleased section title with a release version number and a release date to the `CHANGELOG.md`, and link the version number to a tag url (tag is created later). Do no leave the title "Unreleased" in the file at this commit.
- Make another commit with the next development version number in the files
  - Add `.post0` suffix to version number in `__init__.py` to indicate new development version
  - Add new unreleased section to the `CHANGELOG.md`
- Merge these two commits to the main branch
- Create a release from the first of these two commits
  - Create a release with a version number title and a `vX.X.X` style tag
  - Action should trigger from the release and build and publish the package to PyPI
