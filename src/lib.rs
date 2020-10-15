use pyo3::create_exception;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};
use rocksdb::{Options, DB};
use std::str;

create_exception!(rocksdb3, RocksDBError, PyRuntimeError);

/// Python bindings for rocksdb.
#[pymodule]
fn rocksdb3(_py: Python, m: &PyModule) -> PyResult<()> {
    /// A RocksDB database.
    #[pyclass]
    struct RocksDB {
        db: DB,
        path: Vec<u8>,
    }

    #[pymethods]
    impl RocksDB {
        /// The path of the database.
        #[getter(path)]
        fn get_path<'py>(&self, py: Python<'py>) -> &'py PyString {
            return PyString::new(py, str::from_utf8(&self.path).unwrap());
        }

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
        match DB::open_default(path) {
            Ok(db) => Ok(RocksDB {
                db: db,
                path: path.as_bytes().to_vec(),
            }),
            Err(e) => {
                return Err(RocksDBError::new_err(format!(
                    "can not open {}: {}",
                    path, e,
                )))
            }
        }
    }

    /// Repair the database cannot be opened.
    ///
    /// If a DB cannot be opened, you may attempt to call this method to
    /// resurrect as much of the contents of the database as possible.
    /// Some data may be lost, so be careful when calling this function
    /// on a database that contains important information.
    ///
    /// Positional arguments:
    /// - `path` (required): Path of the database to repair.
    #[pyfn(m, "repair")]
    fn repair(path: &str) -> PyResult<()> {
        match DB::repair(&Options::default(), path) {
            Ok(()) => Ok(()),
            Err(e) => {
                return Err(RocksDBError::new_err(format!(
                    "can not repair {}: {}",
                    path, e,
                )))
            }
        }
    }

    /// Destroy the contents of the specified database.
    /// **Be very careful using this method.**
    ///
    /// Positional arguments:
    /// - `path` (required): Path of the database to destroy.
    #[pyfn(m, "destroy")]
    fn destroy(path: &str) -> PyResult<()> {
        match DB::destroy(&Options::default(), path) {
            Ok(()) => Ok(()),
            Err(e) => {
                return Err(RocksDBError::new_err(format!(
                    "can not destroy {}: {}",
                    path, e,
                )))
            }
        }
    }

    m.add_class::<RocksDB>()?;
    m.add("RocksDBError", _py.get_type::<RocksDBError>())?;
    Ok(())
}
