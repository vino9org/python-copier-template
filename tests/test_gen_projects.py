import os
import os.path
import random
import shlex
import shutil
import subprocess
from pathlib import Path

import yaml
from copier import run_copy

cwd = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.abspath(os.path.join(cwd, ".."))


def run_pytest_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("rye sync"))
        assert subprocess.call(shlex.split("rye run pytest -v -s")) == 0
    finally:
        os.chdir(current_path)


def run_linting_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("rye sync"))
        # run ruff but ignore formatting realted errors
        # some formatting, import related errors can be fixed automatically
        # so we ignore them here
        # I001: Missing docstring in public module.
        # E302: Expected 2 blank lines, found 1.
        # E303: Too many blank lines (found 2).
        # W291: Trailing whitespace.
        # W292: No newline at end of file.
        # W391: Blank line at end of file.
        # F401: Module imported but unused.
        result = subprocess.run(
            shlex.split("rye run ruff check . --ignore I001,E302,E303,W291,W292,W391,F401 --verbose"),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"==RUFF output===\n{result.stdout}"

        if os.environ.get("SKIP_MYPY", "0") != "1":
            result = subprocess.run(
                shlex.split("rye run mypy ."),
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"==MYPY output===\n{result.stdout}"

    finally:
        os.chdir(current_path)


def run_precommit_in_generated_project(project_path):
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("rye sync"))
        assert subprocess.call(shlex.split("rye run pre-commit install")) == 0

        # is adding a file necceeary?
        with open("a.py", "w") as f:
            f.write("# just some text\n")
            f.write("some_var = 0\n")
        assert subprocess.call(shlex.split("git add a.py")) == 0

        assert subprocess.call(shlex.split("rye run pre-commit run")) == 0
    finally:
        os.chdir(current_path)


def check_project_structure(project_path, answers):
    use_docker = answers["use_docker"]
    use_devcontainer = answers["use_devcontainer"]
    use_github_action = answers["use_github_action"]
    project_type = answers["project_type"]
    db_type = answers["db_type"]

    assert (project_path / ".git/HEAD").is_file()

    if use_devcontainer:
        assert (project_path / ".devcontainer").is_dir()
        assert (project_path / "devcontainer.json").is_file()
    else:
        assert not (project_path / ".devcontainer").exists()

    if use_docker:
        assert (project_path / "Dockerfile").is_file()
        assert (project_path / "entrypoint.sh").is_file()
    else:
        assert not (project_path / "Dockerfile").exists()
        assert not (project_path / "entrypoint.sh").exists()

    if use_github_action:
        assert (project_path / ".github").is_dir()
    else:
        assert not (project_path / ".github").exists()

    if project_type != "django" and db_type != "none":
        assert (project_path / "alembic.ini").is_file()
        assert (project_path / "migrations").is_dir()
        assert (project_path / "tests/test_models.py").is_file()

    if project_type == "django" or db_type == "none":
        assert not (project_path / "alembic.ini").exists()
        assert not (project_path / "migrations").exists()
        assert (project_path / "tests/test_models.py").exists()

    if project_type == "fastapi":
        assert (project_path / "main.py").is_file()
        assert (project_path / "database.py").is_file()
    else:
        assert not (project_path / "main.py").exists()
        assert not (project_path / "database.py").exists()


def test_generate_and_build(data: dict, tmp_path: Path):
    suffix = str(random.randint(1, 100))
    dst_path = tmp_path / f"p{suffix}"

    try:
        run_copy(template_path, dst_path, data=data)
        assert (dst_path / "._copier-anwers.yml").is_file()

        check_project_structure(dst_path)
        run_pytest_in_generated_project(dst_path)
        run_linting_in_generated_project(dst_path)
        run_precommit_in_generated_project(dst_path)
    finally:
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)


def test_rendered_project(tmp_path: Path):
    dst_path = Path("/Users/lee/tmp/ttt")
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)

    answers = read_answer(cwd + "/answers/fastapi_async.yml")
    result = run_copy(template_path, dst_path, data=answers, unsafe=True)

    assert (dst_path / ".copier-answers.yml").is_file()

    check_project_structure(dst_path, answers)
    run_pytest_in_generated_project(dst_path)
    run_linting_in_generated_project(dst_path)
    run_precommit_in_generated_project(dst_path)

    print(result)


def read_answer(file_path):
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data
