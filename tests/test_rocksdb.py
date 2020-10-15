import sys
from pathlib import Path

import pytest

try:
    import rocksdb3
except ModuleNotFoundError:
    print("Run `maturin develop` first.", file=sys.stderr)
    raise


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))
    return db


def test_open_default(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))

    assert db.get(b'open') is None


def test_open_again_should_raises_an_error(tmp_path):
    db_path = tmp_path / 'db'
    _ = rocksdb3.open_default(str(db_path))

    with pytest.raises(rocksdb3.RocksDBError) as excinfo:
        rocksdb3.open_default(str(db_path))

    assert 'can not open' in str(excinfo.value)


def test_auto_close(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))

    del db

    assert rocksdb3.open_default(str(db_path)) is not None


def test_put_and_get(db):
    db.put(b'hello', b'world')

    assert db.get(b'hello') == b'world'


def test_key_must_be_bytes(db):
    with pytest.raises(TypeError):
        db.put('notbytes', b'')


def test_value_must_be_bytes(db):
    with pytest.raises(TypeError):
        db.put(b'bytes', 'notbytes')


def test_delete(db):
    db.put(b'hello', b'world')
    assert db.get(b'hello') is not None

    db.delete(b'hello')

    assert db.get(b'hello') is None


def test_destroy(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))
    path = db.path
    del db
    assert Path(path).exists()

    rocksdb3.destroy(path)

    assert not Path(path).exists()
