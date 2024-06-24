import sys
from pathlib import Path
from typing import Iterator

import pytest

tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir.parent))


@pytest.fixture(scope="session")
def testdata_path() -> Iterator[Path]:
    yield tests_dir / "data"


@pytest.fixture(scope="session")
def template_dir() -> Iterator[str]:
    # Copier template path must be a str
    yield str(tests_dir.parent)
