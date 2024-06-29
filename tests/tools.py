# generated project validators used by the test cases
import itertools
import os
import os.path
import shlex
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import yaml


def prefix_in_list(mylist: list[str], prefix: str) -> bool:
    return any(item.startswith(prefix) for item in mylist)


def yaml2dict(file_path: Path) -> dict[str, Any]:
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


def pyproject_dependencies(project_path: Path, include_dev: bool = False) -> list[str]:
    # Open and parse the pyproject.toml file
    with open(project_path / "pyproject.toml", "rb") as toml_f:
        pyproject_data = tomllib.load(toml_f)

    dependencies = pyproject_data.get("project", {}).get("dependencies", [])
    if include_dev:
        dependencies += pyproject_data.get("tool.rye", {}).get("dev-dependencies", [])

    return dependencies


def run_pytest_in_project(project_path: Path) -> None:
    if not os.path.isdir(project_path):
        return

    current_path = os.getcwd()

    try:
        os.chdir(project_path)

        subprocess.call(shlex.split("rye sync"))
        assert subprocess.call(shlex.split("rye run pytest -v -s")) == 0
    finally:
        os.chdir(current_path)


def run_linting_in_project(project_path: Path, run_mypy: bool) -> None:
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
            shlex.split(
                "rye run ruff check . --ignore I001,E302,E303,W291,W292,W391,F401 --verbose"  # noqa
            ),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"==RUFF output===\n{result.stdout}"

        if run_mypy:
            result = subprocess.run(
                shlex.split("rye run mypy ."),
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"==MYPY output===\n{result.stdout}"

    finally:
        os.chdir(current_path)


def run_precommit_in_project(project_path: Path) -> None:
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


def check_project_dependencies(project_path: Path, answers: dict[str, Any]) -> None:
    project_type = answers["project_type"]
    db_type = answers["db_type"]

    dependencies = pyproject_dependencies(project_path, include_dev=True)
    # randomly pick one depdency to check
    assert prefix_in_list(dependencies, "pytest-dotenv")

    if project_type == "quart":
        assert prefix_in_list(dependencies, "quart")
        assert prefix_in_list(dependencies, "flask-orjson")
    elif project_type == "simple":
        assert not prefix_in_list(dependencies, "quart")

    if db_type == "postgresql":
        assert prefix_in_list(dependencies, "tortoise-orm[asyncpg]")
        assert prefix_in_list(dependencies, "aerich")
    elif db_type == "sqlite":
        assert prefix_in_list(dependencies, "tortoise-orm")
        assert not prefix_in_list(dependencies, "tortoise-orm[asyncpg]")
        assert prefix_in_list(dependencies, "aerich")
    elif db_type == "none":
        assert not prefix_in_list(dependencies, "tortoise-orm")
        assert not prefix_in_list(dependencies, "aerich")


def check_project_structure(project_path: Path, answers: dict[str, Any]) -> None:
    use_docker = answers["use_docker"]
    use_devcontainer = answers["use_devcontainer"]
    use_github_action = answers["use_github_action"]
    db_type = answers["db_type"]

    assert (project_path / ".git/HEAD").is_file()

    if use_devcontainer:
        assert (project_path / ".devcontainer").is_dir()
        assert (project_path / ".devcontainer/devcontainer.json").is_file()
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

    if db_type != "none":
        # TODO: assert aerich section in pyproject.toml
        assert (project_path / "tests/test_models.py").is_file()


def scenario_id(scenario: dict[str, Any]) -> str:
    skip_build, data = scenario["skip_build"], scenario["data"]
    sid = "NB" if skip_build else "B"
    sid += f"-{data["project_type"]}-{data["db_type"]}"
    sid += f"-docker({"Y" if data["use_docker"] else "N"})"
    sid += f"-devcontainer({"Y" if data["use_devcontainer"] else "N"})"
    sid += f"-action({"Y" if data["use_github_action"] else "N"})"
    return sid


def enumerate_test_scenarios() -> dict[str, dict[str, Any]]:
    """
    read parameters from copier.yaml and generate all possible combinations
    filter out the combination that should not be tested then return a dict
    with key as the test id and value is context for generation
    """
    # since this function is called during pytest_generate_tests,
    # the fixture values are not available, so we need to read the values
    # directory
    template_path = Path(__file__).parent.parent

    fixed_values = {
        "project_name": "Test Project",
        "pkg_name": "my_pkg",
        "version": "0.1.1",
        "use_docker": False,
        "use_devcontainer": False,
        "use_github_action": False,
    }

    config = yaml2dict(template_path / "copier.yml")
    # remove keys starting with "_", they're used by Coper
    config = {k: v for k, v in config.items() if not k.startswith("_")}

    # remove keys that does only affects some files and directory
    # but does not affect the important content, i.e. dependencies, python files etc
    config = {k: v for k, v in config.items() if k not in fixed_values.keys()}
    options = {k: v["choices"] for k, v in config.items()}

    # generate all possible combinations for remaining keys
    # then add fixed_values to complete the values required
    combinations = list(itertools.product(*list(options.values())))
    scenarios = [
        {**dict(zip(options.keys(), combo)), **fixed_values} for combo in combinations
    ]
    build_group = [{"skip_build": False, "data": entry} for entry in scenarios]

    # generation all combination of 3 boolean options
    # then added to simple.yml to test all combinations of 3 bool values
    simple_data = yaml2dict(template_path / "tests/data/simple.yml")
    bool_values = [True, False]
    bool_combinations = list(itertools.product(bool_values, repeat=3))
    use_xxx_scenarios = [
        {
            **simple_data,
            **dict(
                zip(
                    [
                        "use_docker",
                        "use_github_action",
                        "use_devcontainer",
                    ],
                    combo,
                )
            ),
        }
        for combo in bool_combinations
    ]
    no_build_group = [{"skip_build": True, "data": entry} for entry in use_xxx_scenarios]

    return {scenario_id(entry): entry for entry in (build_group + no_build_group)}
