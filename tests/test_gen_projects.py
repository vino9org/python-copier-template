import os
import os.path
import platform
import random
import shutil
from pathlib import Path

import pytest
from copier import run_copy

from tests.tools import (
    check_project_structure,
    enumerate_test_scenarios,
    run_linting_in_project,
    run_precommit_in_project,
    run_pytest_in_project,
    yaml2dict,
)


def test_generate_and_build(
    generator_ctx,
    template_dir: str,
    tmp_path: Path,
    skip_build: bool = False,
):
    """
    run copier to generate a project, then perform the following checks:
    1. check generate directory structure
    2. check generated dependies in pyproject.toml
    when skip_build is True the following will also be checked:
    3. run pytest
    4. run linting tools, i.e. ruff and mypy
    5. add a random file then run pre-commit
    """
    suffix = str(random.randint(1, 100))
    dst_path = tmp_path / f"p{suffix}"

    try:
        run_copy(template_dir, dst_path, data=generator_ctx, unsafe=True)

        assert (dst_path / "pyproject.toml").is_file()

        check_project_structure(dst_path, generator_ctx)

        if not skip_build:
            if generator_ctx["project_type"] != "django":
                # django project needs to run djang-admin startproject first
                # conftest.py won't work before the project is initialized
                run_pytest_in_project(dst_path)
            run_linting_in_project(dst_path, run_mypy=False)
            run_precommit_in_project(dst_path)

    except ValueError as e:
        if str(e).startswith("Invalid choice"):
            # wrong answer file, just ignore
            pass
        else:
            raise
    except Exception as e:
        print(e)
        raise
    finally:
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)


def pytest_generate_tests(metafunc):
    if "generator_ctx" in metafunc.fixturenames:
        #  generate all test scenarios
        scenarios = enumerate_test_scenarios()
        metafunc.parametrize(
            "generator_ctx",
            scenarios.values(),
            ids=scenarios.keys(),
        )


# do not run this unless doing local development
@pytest.mark.skipif(platform.system() != "Darwin", reason="used for local testing only")
def test_one_project(template_dir, testdata_path):
    dst_path = Path(os.path.expanduser("~/tmp/ttt"))
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)

    answers = yaml2dict(testdata_path / "test_one_project.yml")

    result = run_copy(template_dir, dst_path, data=answers, unsafe=True)

    assert result
    assert (dst_path / ".copier-answers.yml").is_file()

    check_project_structure(dst_path, answers)
    run_pytest_in_project(dst_path)
    run_linting_in_project(dst_path, run_mypy=False)  # mypy is too slow
    run_precommit_in_project(dst_path)
