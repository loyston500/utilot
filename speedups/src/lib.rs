use pyo3;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyDict};
use pyo3::wrap_pyfunction;

use lazy_static::lazy_static;
use std::collections::HashMap;

mod cmdutils;

create_exception!(cmdutils, PyStringScanEOFError, PyException);
create_exception!(cmdutils, PyEscapeSeqEOFError, PyException);
create_exception!(cmdutils, PyPatScanEOFError, PyException);
create_exception!(cmdutils, PyPatZeroLengthError, PyException);

#[pyfunction]
fn py_cmdtokenize(py: Python, source: String) -> PyResult<Vec<PyObject>> {
    let chars = source.chars().collect::<Vec<char>>();
    let tokens = match cmdutils::tokenize(chars) {
        Ok(ok) => ok,
        Err(err) => {
            return match err {
                cmdutils::TokenizerError::StringScanEOF(j) => Err(PyStringScanEOFError::new_err(j)),
                cmdutils::TokenizerError::EscapeSeqEOF(j) => Err(PyEscapeSeqEOFError::new_err(j)),
                cmdutils::TokenizerError::PatScanEOF(j) => Err(PyPatScanEOFError::new_err(j)),
                cmdutils::TokenizerError::PatZeroLength(j) => Err(PyPatZeroLengthError::new_err(j)),
            };
        }
    };

    let mut ret = Vec::new();

    for token in tokens.iter() {
        match token {
            cmdutils::Token::PartialOp(tok) => {
                if tok.len() == 1 {
                    let ch = tok.chars().next().unwrap();
                    ret.push((ch as u32).to_object(py));
                } else {
                    match tok.as_str() {
                        "1>" => ret.push(4962.to_object(py)),
                        "2>" => ret.push(5062.to_object(py)),
                        _ => panic!(format!("bad shit {}", tok)),
                    }
                }
            }
            cmdutils::Token::Str(tok) => {
                ret.push(tok.to_object(py));
            }
        }
    }

    Ok(ret)
}

fn init_cmdutils(py: &Python, m: &PyModule) -> PyResult<()> {
    m.add("tokenize", wrap_pyfunction!(py_cmdtokenize, m)?)?;

    m.add("StringScanEOFError", py.get_type::<PyStringScanEOFError>())?;
    m.add("EscapeSeqEOFError", py.get_type::<PyEscapeSeqEOFError>())?;
    m.add("PatScanEOFError", py.get_type::<PyPatScanEOFError>())?;
    m.add("PatZeroLengthError", py.get_type::<PyPatZeroLengthError>())?;

    Ok(())
}

mod argutils;

create_exception!(argutils, PyInitError, PyException);
create_exception!(argutils, PyValueNotFoundError, PyException);
create_exception!(argutils, PyArgNotFoundError, PyException);

#[pyfunction]
fn py_argparse(
    py: Python,
    list: Vec<String>,
    py_arg_infos: Vec<PyObject>,
) -> PyResult<(HashMap<String, String>, Vec<String>)> {
    let mut arg_infos = Vec::new();

    for py_arg_info in py_arg_infos.iter() {
        let py_arg_info: &PyList = py_arg_info.extract(py)?;
        arg_infos.push(argutils::ArgInfo::new(
            py_arg_info.get_item(0).extract::<Vec<String>>()?,
            py_arg_info.get_item(1).extract::<String>()?,
            py_arg_info.get_item(2).extract::<Option<String>>()?,
            py_arg_info.get_item(3).extract::<bool>()?,
            py_arg_info.get_item(4).extract::<bool>()?,
        ));
    }

    match argutils::parser(list, arg_infos) {
        Ok(ok) => return Ok(ok),
        Err(err) => {
            return match err {
                argutils::ParserError::Init(s) => Err(PyInitError::new_err(s)),
                argutils::ParserError::ValueNotFound(n) => Err(PyValueNotFoundError::new_err(n)),
                argutils::ParserError::ArgNotFound(n) => Err(PyArgNotFoundError::new_err(n)),
            };
        }
    }
}

fn init_argutils(py: &Python, m: &PyModule) -> PyResult<()> {
    m.add("argparse", wrap_pyfunction!(py_argparse, m)?)?;

    m.add("InitError", py.get_type::<PyInitError>())?;
    m.add("ArgNotFoundError", py.get_type::<PyArgNotFoundError>())?;
    m.add("ValueNotFoundError", py.get_type::<PyValueNotFoundError>())?;
    Ok(())
}

/*
#[pyfunction]
fn py_fmt(mut source: String, prefix: String, dict: &PyDict) -> PyResult<String> {
    for (key, value) in dict.iter() {
        let key = key.extract::<String>()?;
        let value = value.extract::<String>()?;
        source = source.replace(prefix + &key, &value); 
    }
    Ok(source)
}
*/


#[pymodule]
fn speedups(py: Python, m: &PyModule) -> PyResult<()> {
    let py_cmdutils = PyModule::new(py, "cmdutils")?;
    init_cmdutils(&py, py_cmdutils)?;
    m.add_submodule(py_cmdutils)?;

    let py_argutils = PyModule::new(py, "argutils")?;
    init_argutils(&py, py_argutils)?;
    m.add_submodule(py_argutils)?;
    
    // m.add("fmt", wrap_pyfunction!(py_fmt, m)?)?;

    Ok(())
}
