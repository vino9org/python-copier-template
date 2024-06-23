
# Welcome to your Python project

This project is set up Python project with dev tooling pre-configured

* ruff
* mypy
* VS Code support

## Setup

The easiest way to get started is use [Visual Studio Code with devcontainer](https://code.visualstudio.com/docs/devcontainers/containers)

[rye](https://github.com/astral-sh/rye) is the blazing fast python project manager tool. Install it first before proceeding.


```shell

# create virtualenv and install dependencies
rye sync

```

## Notes for FastApi - SqlAlchemy options
When selected, a project skeleton of web application with FastApi with SqlAlchmey will be generated, as long with PostgreSQL driver and related setup. The template supports PostgreSQL and SQLite. Other
database supports can be added easiy. Some modification to ```tests/conftest.py``` might be needed.

```shell

# create database and assign proper privileges to the user
# e.g.
# create database mydb;
# grant all privileges on database mydb to me;

# 1. create a .env file with database related setting
#    and edit content. the template supports PostgreSQL and SQLite.
cp env_example .env
nano .env

alembic upgrade head

# run unit tests
pytest -s -v

# the generated code uses sync database drivers. If async support is desirted
# please open ```database.py```, ```tests/conftest.py``` and ```main.py```
# remove the sync db setup code and uncomment the async setup


```

## generate code using config file without interactive input

Create a [config file](sample_prog.json) with options to use, then

```shell

cat <<EOF > config.json
{
    "default_context": {
        "project_name": "Some Program",
        "project_slug": "some_prog",
        "pkg_name": "some_prog",
        "project_short_description": "Some python program",
        "dockerfile_option": "Dockerfile with Github workflow",
        "extra_packages": "None",
        "version": "0.1.0"
    }
}
EOF


cookiecutter gh:vino9org/cookiecutter-python --config-file config.json --no-input

```
