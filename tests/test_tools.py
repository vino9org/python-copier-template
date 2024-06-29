from tests.tools import (
    enumerate_test_scenarios,
    prefix_in_list,
    pyproject_dependencies,
    yaml2dict,
)


def test_prefix_in_list():
    assert prefix_in_list(["quart", "tortoise-orm"], "quart")
    assert prefix_in_list(["quart", "tortoise-orm"], "tortoise")
    assert not prefix_in_list(["quart", "tortoise-orm"], "dangerou")


def test_check_dependency(testdata_path):
    dependecnies = pyproject_dependencies(testdata_path / "dummy")

    assert len(dependecnies) > 3
    assert prefix_in_list(dependecnies, "fastapi")
    assert not prefix_in_list(dependecnies, "blah_blah")


def test_read_yaml(testdata_path):
    data = yaml2dict(testdata_path / "quart_pg.yml")
    assert data["project_type"] == "quart"


def test_enumerate_test_scenarios():
    scenarios = enumerate_test_scenarios()
    assert len(scenarios) > 2  # 20 as of the latest commit
