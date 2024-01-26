use crate::{default_env, parse_eval, LispError, LispExpr};

#[allow(dead_code)]
fn eval(str: &str) -> Result<LispExpr, LispError> {
    parse_eval(str.to_string(), &mut default_env())
}

#[test]
fn test_add() {
    assert_eq!(eval("(+ 1 2)").unwrap(), LispExpr::Number(3.0));
}

#[test]
fn test_sub() {
    assert_eq!(eval("(- 1 2)").unwrap(), LispExpr::Number(-1.0));
}

#[test]
fn test_list() {
    assert_eq!(eval("(- 1 2 (+ 1 2))").unwrap(), LispExpr::Number(-4.0));
}
