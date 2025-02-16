import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def cleanup_files():
    """Cleanup created files after each test"""
    yield
    for path in Path(".").glob("output.*"):
        path.unlink()
