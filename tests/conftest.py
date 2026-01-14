import sys
from pathlib import Path
import pytest
import os

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """
    Ensure required env vars exist for tests.
    """
    os.environ.setdefault("JWT_SECRET", "test-secret-key")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
