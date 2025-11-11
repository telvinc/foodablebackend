import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from main import app
import pytest

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
