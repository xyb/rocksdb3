use pyo3::class::iter::PyIterProtocol;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyTuple};
use rocksdb::{DBIterator, IteratorMode, DB};
use std::sync::Arc;

// stabilize drop order, see https://github.com/rust-lang/rfcs/blob/246ff86b320a72f98ed2df92805e8e3d48b402d6/text/1857-stabilize-drop-order.md
struct UnsafeDBIterator {
    inner: DBIterator<'static>,
    _db: Arc<DB>,
}

impl UnsafeDBIterator {
    fn new(db: Arc<DB>) -> UnsafeDBIterator {
        let iter =
            unsafe { std::mem::transmute(db.iterator(IteratorMode::Start)) };
        UnsafeDBIterator {
            inner: iter,
            _db: db,
        }
    }
}

#[pyclass]
pub struct RocksDBIterator {
    iter: UnsafeDBIterator,
}

impl RocksDBIterator {
    pub fn new(db: Arc<DB>) -> RocksDBIterator {
        RocksDBIterator {
            iter: UnsafeDBIterator::new(db),
        }
    }
}

#[pyproto]
impl PyIterProtocol for RocksDBIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<Self>) -> PyResult<Option<PyObject>> {
        let iter = slf.iter.inner.next();
        for (key, value) in iter {
            let py = slf.py();
            return Ok(Some(
                PyTuple::new(
                    py,
                    &[
                        PyBytes::new(py, key.as_ref()),
                        PyBytes::new(py, value.as_ref()),
                    ],
                )
                .into_py(py),
            ));
        }
        return Ok(None);
    }
}
