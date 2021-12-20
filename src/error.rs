use pyo3::create_exception;
use pyo3::exceptions::PyRuntimeError;

create_exception!(rocksdb3, RocksDBError, PyRuntimeError);
