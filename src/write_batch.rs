use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};
use rocksdb::{WriteBatch as RocksDBWriteBatch};

/// An atomic batch of write operations.
#[pyclass]
pub struct WriteBatch {
    pub batch: RocksDBWriteBatch,
}

#[pymethods]
impl WriteBatch {
    #[new]
    pub fn new(_py: Python) -> PyResult<Self> {
        Ok(WriteBatch {
            batch: RocksDBWriteBatch::default(),
        })
    }

    /// Insert a "value" into the database under the given "key".
    /// If "key" already exists, it will be overwritten.
    ///
    /// Positional arguments:
    /// - `key` (required): Name for this entry.
    /// - `value` (required): Data for this entry.
    fn put(&mut self, key: &PyBytes, value: &PyBytes) -> PyResult<()> {
        self.batch.put(key.as_bytes(), value.as_bytes());
        Ok(())
    }

    /// Remove the database entry for "key".
    /// Does nothing if the key was not found.
    ///
    /// Positional arguments:
    /// - `key` (required): Name to delete.
    fn delete(&mut self, key: &PyBytes) -> PyResult<()> {
        self.batch.delete(key.as_bytes());
        Ok(())
    }
}
