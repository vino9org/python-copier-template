import os
from pathlib import Path
from typing import Sequence

import pytest
from copier import run_copy

cwd = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.abspath(os.path.join(cwd, "../.."))


def test_rendered_project(tmp_path: Path):
    dst_path = "/Users/lee/tmp/ttt"
    if os.path.exists(dst_path):
        os.rmdir(dst_path)

    result = run_copy(template_path, dst_path)

    print(result)
