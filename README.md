
# Copier template for python project

This a [Copier](https://copier.readthedocs.io/en/stable/) template generates a python project with ready to go ```pyproject.toml``` configuration for pytest, linting tools.

* [ruff](https://docs.astral.sh/ruff/)
* [mypy](https://github.com/python/mypy)
* VS Code support

## Project Options
The template supports the following application types with or without database drivers. If database driver is chosen, ```conftest.py``` will contain test databae preparation fixtures.

* simple
* [fastapi](https://fastapi.tiangolo.com/)
* [django](https://www.djangoproject.com/)

For FastApi project, if a database driver is chosen, sqlalchemy and alembic will be included. Async db driver support is also included.

For django project, ```django-admin startproject``` needs to be run manually before test cases will run.

The following dev tooling are supported:
* vscode
* ruff
* mypy
* devcontainer
* Dockerfile
* GitHub action for unit test and container image creation

## generate code using config file without interactive input

Create a ```config.yml``` with options to use, then

```shell

cat <<EOF > config.yaml
asyncio_db: true
db_type: postgresql
pkg_name: myt
project_name: My Test Proj
project_type: fastapi
use_devcontainer: false
use_docker: false
use_github_action: false
version: 0.1.0
EOF


pipx run copier gh:vino9org/python-copier-template output_dir -a config.yaml --trust

```

## Developer notes
The unit test code contains logic to automatically generate test cases for various configuration options and run test against each of them, in order to guide the templaet from acciental break. See [tests/tools.py](tests/tools.py) for more details.
