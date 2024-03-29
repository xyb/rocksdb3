import sys
from pathlib import Path

import pytest

try:
    import rocksdb3
except ModuleNotFoundError:
    print('Run `maturin develop` first.', file=sys.stderr)
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
    assert db_secondary.get(b'author') is None
    db_primary.put(b'author', b'xyb')

    db_secondary.try_catch_up_with_primary()

    assert db_secondary.get(b'author') == b'xyb'


def test_open_with_ttl(tmp_path):
    db_path = tmp_path / 'ttl'
    db = rocksdb3.open_with_ttl(str(db_path), int(60))

    assert db.get(b'open_with_ttl') is None


def test_batch_put(tmp_path):
    db_path = tmp_path / 'batch_put'
    db = rocksdb3.open_default(str(db_path))
    assert db.get(b'batch_put_1') is None

    batch = rocksdb3.WriterBatch()
    batch.put(b'batch_put_1', b'yes_1')
    batch.put(b'batch_put_2', b'yes_2')
    assert db.get(b'batch_put_1') is None
    db.write(batch)

    assert db.get(b'batch_put_1') == b'yes_1'


def test_batch_delete(tmp_path):
    db_path = tmp_path / 'batch_delete'
    db = rocksdb3.open_default(str(db_path))
    db.put(b'hello', b'world')
    db.put(b'foo', b'bar')

    batch = rocksdb3.WriterBatch()
    batch.delete(b'hello')
    batch.delete(b'foo')
    assert db.get(b'hello') is not None
    assert db.get(b'foo') is not None
    db.write(batch)

    assert db.get(b'hello') is None
    assert db.get(b'foo') is None


def test_batch_clear(tmp_path):
    db_path = tmp_path / 'batch_clear'
    db = rocksdb3.open_default(str(db_path))
    db.put(b'hello', b'world')
    db.put(b'foo', b'bar')

    batch = rocksdb3.WriterBatch()
    batch.delete(b'hello')
    batch.put(b'foo', b'foo')
    batch.clear()
    db.write(batch)

    assert db.get(b'hello') == b'world'
    assert db.get(b'foo') == b'bar'
