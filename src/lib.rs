use pyo3::create_exception;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rocksdb::DB;

create_exception!(rocksdb3, RocksDBError, PyRuntimeError);

/// Python bindings for rocksdb.
#[pymodule]
fn rocksdb3(_py: Python, m: &PyModule) -> PyResult<()> {
    /// A RocksDB database.
    #[pyclass]
    struct RocksDB {
        db: DB,
    }

    #[pymethods]
    impl RocksDB {
        /// Return the bytes associated with a key value.
        ///
        /// Positional arguments:
        /// - `key` (required): Name to get.
        fn get<'py>(
            &mut self,
            py: Python<'py>,
            key: &PyBytes,
        ) -> PyResult<Option<&'py PyBytes>> {
            match self.db.get(key.as_bytes()) {
                Ok(Some(value)) => Ok(Some(PyBytes::new(py, &value))),
                Ok(None) => return Ok(None),
                Err(e) => {
                    return Err(RocksDBError::new_err(format!(
                        "can not get key {}: {}",
                        key, e,
                    )))
                }
            }
        }

        /// Set the database entry for "key" to "value".
        /// If "key" already exists, it will be overwritten.
        ///
        /// Positional arguments:
        /// - `key` (required): Name for this entry.
        /// - `value` (required): Data for this entry.
        fn put(&mut self, key: &PyBytes, value: &PyBytes) -> PyResult<()> {
            match self.db.put(key.as_bytes(), value.as_bytes()) {
                Ok(_) => Ok(()),
                Err(e) => {
                    return Err(RocksDBError::new_err(format!(
                        "can not put key {}: {}",
                        key, e,
                    )))
                }
            }
        }

        /// Remove the database entry for "key".
        ///
        /// Positional arguments:
        /// - `key` (required): Name to delete.
        fn delete(&mut self, key: &PyBytes) -> PyResult<()> {
            match self.db.delete(key.as_bytes()) {
                Ok(_) => Ok(()),
                Err(e) => {
                    return Err(RocksDBError::new_err(format!(
                        "can not delete key {}: {}",
                        key, e,
                    )))
                }
            }
        }
    }

    /// Opens a database with default options.
    ///
    /// Positional arguments:
    /// - `path` (required): Path of the database to open.
    #[pyfn(m, "open_default")]
    fn open_default(path: &str) -> PyResult<RocksDB> {
        match DB::open_default(&path) {
            Ok(db) => Ok(RocksDB { db: db }),
            Err(e) => {
                return Err(RocksDBError::new_err(format!(
                    "can not open {}: {}",
                    path, e,
                )))
            }
        }
    }

    m.add_class::<RocksDB>()?;
    m.add("RocksDBError", _py.get_type::<RocksDBError>())?;
    Ok(())
}
