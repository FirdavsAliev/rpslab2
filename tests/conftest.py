import pytest
import db

TEST_DB = "test_fitness.db"

@pytest.fixture
def test_db(tmp_path):
    path = str(tmp_path / TEST_DB)
    db.init_db(path)
    yield path