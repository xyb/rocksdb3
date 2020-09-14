try:
    import rocksdb
except ModuleNotFoundError:
    print("Run `maturin develop` first.", file=sys.stderr)
    raise


def test_open_default(tmp_path):
    db_path = tmp_path / 'db'

    db = rocksdb.open_default(str(db_path))

    assert db.get(b'open') is None


def test_put_and_get(tmp_path):
    db_path = tmp_path / 'put'
    db = rocksdb.open_default(str(db_path))

    db.put(b'hello', b'world')

    assert db.get(b'hello') == b'world'


def test_delete(tmp_path):
    db_path = tmp_path / 'delete'
    db = rocksdb.open_default(str(db_path))
    db.put(b'hello', b'world')
    assert db.get(b'hello') is not None

    db.delete(b'hello')

    assert db.get(b'hello') is None


