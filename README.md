# Python bindings for rocksdb

Rocksdb3 is a python bindings for
[rocksdb](https://github.com/facebook/rocksdb) based on rust wrapper
[rust-rocksdb](https://github.com/rust-rocksdb/rust-rocksdb) and
[PyO3](https://github.com/PyO3/pyo3).

This is a very early proof-of-concept version.
Please do not use it in production.

[![Actions Status](https://github.com/xyb/rocksdb3/workflows/tests/badge.svg?branch-master)](https://github.com/xyb/rocksdb3/actions)
[![Latest version](https://img.shields.io/pypi/v/rocksdb3.svg)](https://pypi.org/project/rocksdb3/)
[![Support python versions](https://img.shields.io/pypi/pyversions/rocksdb3.svg)](https://pypi.org/project/rocksdb3/)
[![License](https://img.shields.io/pypi/l/rocksdb3.svg)](https://github.com/xyb/rocksdb3/blob/master/LICENSE)

## Status
  - [x] basic open/put/get/delete/close
  - [ ] iterator
  - [ ] write batch
  - [ ] destroy/repair

## Install
```
pip install rocksdb3
```

## Examples

```python
import rocksdb3

db = rocksdb3.open_default('db_path')
assert db.get(b'my key') is None
db.put(b'my key', b'my value')
assert db.get(b'my key') == b'my value'
db.delete(b'my key')
assert db.get(b'my key') is None
del db  # auto close db
```

## build

```
pip install maturin
maturin build
```
