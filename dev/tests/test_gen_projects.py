import yaml
import os
import shutil
from pathlib import Path
from typing import Sequence

import pytest
from copier import run_copy

cwd = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.abspath(os.path.join(cwd, "../.."))


def test_rendered_project(tmp_path: Path):
    dst_path = "/Users/lee/tmp/ttt"
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)

    answer_data = read_answer(cwd + "/fastapi_async.yml")
    result = run_copy(template_path, dst_path, data=answer_data)

    print(result)


def read_answer(file_path):
    with open(file_path, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data
