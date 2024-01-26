mod test;

use std::{
    collections::HashMap,
    io::{self, Write},
    process::exit,
};

#[derive(Clone, Debug, PartialEq)]
// LispExpr枚举类型，表示表达式，包含四种形式：符号、数字、列表和函数
pub enum LispExpr {
    Symbol(String),                                       // 符号形式，参数为字符串
    Number(f64),                                          // 数字形式，参数为f64类型
    List(Vec<LispExpr>),                                  // 列表形式，参数为LispExpr的切片
    Func(fn(&[LispExpr]) -> Result<LispExpr, LispError>), // 函数形式，参数为LispExpr的数组，返回LispExpr或LispError
}

#[derive(Clone, Debug)]
// LispError结构体，表示表达式计算过程中的错误
pub enum LispError {
    Reason(String), // 原因形式，参数为字符串
}

#[derive(Clone, Debug, PartialEq)]
// LispEnv结构体，表示表达式的环境，包含一个哈希表用于存储符号和表达式的映射关系
pub struct LispEnv {
    pub data: HashMap<String, LispExpr>, // 哈希表，用于存储符号和表达式的映射关系
}

// 将源代码字符串转换为token列表
pub fn tokenize(source_code: String) -> Vec<String> {
    source_code
        .replace('(', " ( ")
        .replace(')', " ) ")
        .split_whitespace()
        .map(|x| x.to_string())
        .collect()
}

// 解析token列表，返回计算结果和剩余的token列表
pub fn parse(tokens: &[String]) -> Result<(LispExpr, &[String]), LispError> {
    let (tok, rest) = tokens
        .split_first()
        .ok_or(LispError::Reason("could not get token".to_string()))?;
    match &tok[..] {
        "(" => read_seq(rest),
        ")" => Err(LispError::Reason(
            "unexpected `)`(tip: unmatched `)` ?)".to_string(),
        )),
        _ => Ok((parse_atom(tok), rest)),
    }
}

// 解析序列中的token列表，返回表达式和剩余的token列表
fn read_seq(tokens: &[String]) -> Result<(LispExpr, &[String]), LispError> {
    let mut res = vec![];
    let mut xs = tokens;
    loop {
        let (next_tok, rest) = xs.split_first().ok_or(LispError::Reason(
            "could not found closing `)`.".to_string(),
        ))?;
        if next_tok == ")" {
            return Ok((LispExpr::List(res), rest));
        }
        let (expr, new_xs) = parse(xs)?;
        res.push(expr);
        xs = new_xs;
    }
}

// 将token解析为原子表达式
fn parse_atom(tok: &str) -> LispExpr {
    let float_parse = tok.parse();
    match float_parse {
        Ok(v) => LispExpr::Number(v),
        Err(_) => LispExpr::Symbol(tok.to_string()),
    }
}

// 计算列表中表达式的浮点数结果列表
fn parse_float_list(args: &[LispExpr]) -> Result<Vec<f64>, LispError> {
    args.iter().map(parse_single_float).collect()
}

// 计算单个表达式的结果
fn parse_single_float(expr: &LispExpr) -> Result<f64, LispError> {
    match expr {
        LispExpr::Number(num) => Ok(*num),
        _ => Err(LispError::Reason("a number is expected.".to_string())),
    }
}

// 创建默认的表达式环境
pub fn default_env() -> LispEnv {
    let mut data = HashMap::new();
    data.insert(
        "+".to_string(),
        LispExpr::Func(|args| -> Result<LispExpr, LispError> {
            let sum = parse_float_list(args)?
                .iter()
                .fold(0.0, |sum, next| sum + next);
            Ok(LispExpr::Number(sum))
        }),
    );
    data.insert(
        "-".to_string(),
        LispExpr::Func(|args| -> Result<LispExpr, LispError> {
            let floats = parse_float_list(args)?;
            let first = *floats
                .first()
                .ok_or(LispError::Reason(
                    "too few arguments were given.".to_string(),
                ))
                .unwrap();
            let sum = floats.iter().skip(1).fold(first, |sum, next| sum - next);
            Ok(LispExpr::Number(sum))
        }),
    );
    data.insert(
        "*".to_string(),
        LispExpr::Func(|args| -> Result<LispExpr, LispError> {
            let sum = parse_float_list(args)?
                .iter()
                .fold(1.0, |sum, next| sum * next);
            Ok(LispExpr::Number(sum))
        }),
    );
    data.insert(
        "/".to_string(),
        LispExpr::Func(|args| -> Result<LispExpr, LispError> {
            let floats = parse_float_list(args)?;
            if floats.contains(&0.0) {
                return Err(LispError::Reason("divide by zero.".to_string()));
            }
            let first = *floats
                .first()
                .ok_or(LispError::Reason(
                    "too few arguments were given.".to_string(),
                ))
                .unwrap();
            let sum = floats.iter().skip(1).fold(first, |sum, next| sum / next);
            Ok(LispExpr::Number(sum))
        }),
    );
    LispEnv { data }
}

// 根据表达式和环境计算表达式结果
pub fn eval(expr: &LispExpr, env: &mut LispEnv) -> Result<LispExpr, LispError> {
    match expr {
        LispExpr::Symbol(name) => env
            .data
            .get(name)
            .ok_or(LispError::Reason(format!("unexpected symbol {name}.")))
            .map(|x| x.clone()),

        LispExpr::Number(_n) => Ok(expr.clone()),

        LispExpr::List(list) => {
            let first_form = list
                .first()
                .ok_or(LispError::Reason("empty list.".to_string()))?;
            let arg_forms = &list[1..];
            let func_v = eval(first_form, env)?;
            if let LispExpr::Func(func) = func_v {
                let args: Result<Vec<LispExpr>, LispError> =
                    arg_forms.iter().map(|x| eval(x, env)).collect();
                func(&args?)
            } else {
                Err(LispError::Reason("first form is not callable.".to_string()))
            }
        }

        LispExpr::Func(_) => Err(LispError::Reason("unexpected form".to_string())),
    }
}

// 读取一行表达式并返回字符串形式的表达式
fn slurp_expr() -> String {
    let mut expr = String::new();
    io::stdout().flush().unwrap();
    io::stdin()
        .read_line(&mut expr)
        .expect("Failed to read line");
    if expr.trim() == ".exit" {
        println!("bye.");
        exit(0);
    }
    expr
}

// 读取一行表达式并计算表达式结果
fn parse_eval(expr: String, env: &mut LispEnv) -> Result<LispExpr, LispError> {
    let (parsed_exp, _) = parse(&tokenize(expr))?;
    let eval_exp = eval(&parsed_exp, env)?;
    Ok(eval_exp)
}

// 运行表达式解释器的REPL
pub fn run_repl() {
    let env = &mut default_env();
    println!("Welcome to Runctional Repl written in Rust. Supports `+`,`-`,`*`,`/` operator.");
    println!("Input `.exit` to quit.");
    loop {
        print!("RunctionalExpr > ");
        let expr = slurp_expr();
        match parse_eval(expr, env) {
            Ok(res) => println!("// Val => `{:?}`", res),
            Err(e) => match e {
                LispError::Reason(msg) => println!("// Err => {}", msg),
            },
        }
    }
}

fn main() {
    run_repl()
}
