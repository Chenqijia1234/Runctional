#[cfg(test)]
use crate::{default_env, parse_eval, LispError, LispExpr};

#[cfg(test)]
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
fn test_mul() {
    assert_eq!(eval("(* 1 2 3)").unwrap(), LispExpr::Number(6.0));
}

#[test]
fn test_div() {
    assert_eq!(eval("(/ 6 2 3)").unwrap(), LispExpr::Number(1.0));
}

#[test]
fn test_list() {
    assert_eq!(
        eval("(+ (- 3 1) (* 1 1) (/ 1 1))").unwrap(),
        LispExpr::Number(4.0)
    );
}

#[test]
fn test_print() {
    assert_eq!(
        eval("(print 3)").unwrap(),
        LispExpr::List(vec![LispExpr::Number(3.0)])
    );
}
