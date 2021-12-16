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


def test_destroy_should_not_delete_db_that_is_in_using(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))

    with pytest.raises(rocksdb3.RocksDBError):
        rocksdb3.destroy(db.path)


def test_repair(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))
    path = db.path
    del db

    rocksdb3.repair(path)


def test_repair_should_not_be_used_on_db_that_is_in_using(tmp_path):
    db_path = tmp_path / 'db'
    db = rocksdb3.open_default(str(db_path))

    with pytest.raises(rocksdb3.RocksDBError):
        rocksdb3.repair(db.path)


def test_iter(db):
    db.put(b'hello', b'world')
    db.put(b'author', b'xyb')
    it = db.get_iter()

    assert next(it) == (b'author', b'xyb')
    assert next(it) == (b'hello', b'world')


def test_secondary(tmp_path):
    primary_path = tmp_path / 'primary'
    db_primary = rocksdb3.open_default(str(primary_path))
    db_primary.put(b'hello', b'world')

    secondary_path = tmp_path / 'secondary'
    db_secondary = rocksdb3.open_as_secondary(str(primary_path),
                                              str(secondary_path))

    assert list(db_secondary.get_iter()) == [(b'hello', b'world')]


def test_secondary_catch_up_primary(tmp_path):
    primary_path = tmp_path / 'primary'
    db_primary = rocksdb3.open_default(str(primary_path))
    secondary_path = tmp_path / 'secondary'
    db_secondary = rocksdb3.open_as_secondary(str(primary_path),
                                              str(secondary_path))
    assert db_secondary.get(b'author') == None
    db_primary.put(b'author', b'xyb')

    db_secondary.try_catch_up_with_primary()

    assert db_secondary.get(b'author') == b'xyb'
