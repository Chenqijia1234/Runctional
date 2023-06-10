"""
作者
    鱼翔浅底 : https://code.xueersi.com/space/32273536
版本要求
    最低Python版本 : Python3.10
参考资料
    Peter Norvig : (How to Write a (Lisp) Interpreter (in Python)) https://norvig.com/lispy.html
    Christian Queinnec : Lisp in Small Pieces
更新计划
    0.0.1 DEV_2 实现模块 + 补充测试用例
    0.0.1 DEV_3 实现字符串 + repl括号匹配与多行输入
    0.0.1 DEV_4 扩充标准库
更新日志
    0.0.1 DEV_1 最小可用版本
    0.0.1 DEV_1_patch_1 修复if语句的恶性bug，补充少许测试
    0.0.1 DEV_1_patch_2 支持尾递归优化
"""
# 参见 https://peps.python.org/pep-0563/
# 这是一个有故事的PEP
from __future__ import annotations

import math
import operator as op
import sys
from collections import ChainMap
from typing import TypeAlias, Any, Final, Union, NamedTuple

__version__ = "0.0.1 DEV_1_patch_2"  # 最小可用版本 + 补丁修复

SourceCode: TypeAlias = str
Symbol: TypeAlias = str
Atom: TypeAlias = Union[int, float, Symbol]
TokenList: TypeAlias = list[Symbol]
Expression: TypeAlias = Union[list[Atom], Atom]
ExpressionList: TypeAlias = list[Expression]

KEYWORDS_1 = ['quote', 'if', 'define', 'lambda']
KEYWORDS_2 = ['set!', 'cond', 'or', 'and', 'begin']
KEYWORDS = KEYWORDS_1 + KEYWORDS_2


class InterpreterConfiguration:
    TailCallOptimizationEnabled: bool = True
    RecursionLimit: int = 10_0000


def init() -> None:
    sys.setrecursionlimit(InterpreterConfiguration.RecursionLimit)


class Environment(ChainMap):
    def change(self, key: Symbol, value: object) -> None:
        for map in self.maps:
            if key == map:
                map[key] = value
                return
        raise KeyError(key)


def lispstr(exp: object) -> str:
    """
    转换python对象为字符串供使用
    """
    if isinstance(exp, list):
        return "(" + " ".join(map(lispstr, exp)) + ")"
    else:
        return str(exp)


class InterpreterException(Exception):
    def __init__(self, value: str = ""):
        self.value = value

    def __str__(self) -> str:
        msg = self.__class__.__doc__ or ""
        if self.value:
            msg = msg.rstrip(".")
            if "'" in self.value:
                value = self.value
            else:
                value = repr(self.value)
            msg += f": {value}"
        return msg


class UnexpectedCloseParentheses(InterpreterException):
    pass


class UnexpectedEndOfSource(InterpreterException):
    pass


class InvalidSyntax(InterpreterException):
    pass


class EvaluatorException(InterpreterException):
    pass


class UndefinedSymbol(InterpreterException):
    pass


class Function:
    def __init__(
            self,
            params: list[Symbol],
            body: list[Expression],
            env: Environment,
            interpreter_instance: Interpreter,
    ) -> None:
        self.params = params
        self.body = body
        self.definition_env = env
        self.interpreter = interpreter_instance

    def application_env(self, *args: list[Expression]) -> Any:
        function_internal_env = dict(zip(self.params, args, strict=True))
        env: Environment = Environment(function_internal_env, self.definition_env)
        return env

    def __call__(self, *args: Expression) -> Any:
        env = self.application_env(*args)
        result = None
        for expr in self.body:
            result = self.interpreter.evaluate(expr, env)
        return result


def standard_env() -> Environment:
    def display(x: Any) -> Any:
        print(x)
        return x

    """
    标准全局环境
    """
    env: Environment = Environment()
    env.update(vars(math))
    env.update(
        {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "%": op.mod,
            "quotient": op.floordiv,
            ">": op.gt,
            "<": op.lt,
            ">=": op.ge,
            "<=": op.le,
            "=": op.eq,
            "abs": abs,
            "append": op.add,
            "apply": lambda proc, args: proc(*args),
            "begin": lambda *x: x[-1],
            "car": lambda x: x[0],
            "cdr": lambda x: x[1:],
            "cons": lambda x, y: [x] + y,
            "eq?": op.is_,
            "equal?": op.eq,
            "filter": lambda *args: list(filter(*args)),
            "length": len,
            "list": lambda *x: list(x),
            "list?": lambda x: isinstance(x, list),
            "map": lambda *args: list(map(*args)),
            "max": max,
            "min": min,
            "not": op.not_,
            "null?": lambda x: x == [],
            "number?": lambda x: isinstance(x, (int, float)),
            "procedure?": callable,
            "round": round,
            "symbol?": lambda x: isinstance(x, Symbol),
            "display": display,
        }
    )
    return env


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source

    def lex(self) -> TokenList:
        """
        奇特(省事)的Lexer实现
        除了不支持注释，不支持字符串，目前还没有什么问题
        """
        return self.source.replace("(", " ( ").replace(")", " ) ").split()


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.tokens = self.lexer.lex()

    @staticmethod
    def parse_atom(token: str) -> Atom:
        """
        获得原谅比获得许可更容易。
        """
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return Symbol(token)

    def read_from_tokens(self, tokens: TokenList) -> ExpressionList:
        """
        自己手写的升级版
        """
        return self._parse_code_structure(tokens)

    def parse(self) -> Expression:
        return self.read_from_tokens(self.tokens)

    def _parse_code_structure(self, tokens) -> ExpressionList:
        def _parse(tokens: list[Symbol]) -> Expression:
            if len(tokens) == 0:
                raise UnexpectedEndOfSource()

            token = tokens.pop(0)

            if "(" == token:
                exp = []
                while tokens and tokens[0] != ")":
                    exp.append(_parse(tokens))
                if not tokens:
                    raise UnexpectedEndOfSource()
                tokens.pop(0)  # ')'
                return exp
            elif ")" == token:
                raise UnexpectedCloseParentheses()
            else:
                return Parser.parse_atom(token)

        result = []
        while len(tokens) > 0:
            result.append(_parse(tokens))
        return result


class Interpreter:
    """
    :since 0.0.1 DEV_1_patch_2 ⭐⭐⭐ 尾递归优化！！！
    """

    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def evaluate(self, expr: Expression, env: Environment) -> Any:
        """
        Python3.10+ 模式匹配!!!
        相关文献
            https://peps.python.org/pep-0634/
            https://peps.python.org/pep-0635/
            https://peps.python.org/pep-0636/
        """
        while True:
            match expr:
                case int(x) | float(x):
                    return x
                case Symbol(var):
                    try:
                        return env[var]
                    except KeyError as err:
                        raise UndefinedSymbol(var) from err
                case ["quote", expr]:
                    return expr
                case ["if", cond, then, else_]:
                    if self.evaluate(cond, env):
                        expr = then
                    else:
                        expr = else_
                case ["set!", Symbol(var), value]:
                    env.change(var, self.evaluate(value, env))
                    return
                case ["define", Symbol(var), value]:
                    env[var] = self.evaluate(value, env)
                    return
                case ["define", [Symbol(func_name), *params], *body] if len(body) > 0:
                    env[func_name] = Function(params, body, env, self)
                    return
                case ["lambda", [*params], *body] if len(body) > 0:
                    return Function(params, body, env, self)
                case ["cond", *expressions]:
                    return self.cond_form(expressions, env)
                case ["or", *expressions]:
                    return self.or_form(expressions, env)
                case ["and", *expressions]:
                    return self.and_form(expressions, env)
                case ["begin", *expressions]:
                    for exp in expressions[:-1]:
                        self.evaluate(exp, env)
                    expr = expressions[-1]
                case [op, *args] if op not in KEYWORDS:
                    proc = self.evaluate(op, env)
                    values = tuple(self.evaluate(arg, env) for arg in args)
                    if InterpreterConfiguration.TailCallOptimizationEnabled and isinstance(proc, Function):
                        expr = ["begin", *proc.body]
                        env = proc.application_env(*values)
                    else:
                        try:
                            return proc(*values)
                        except TypeError as err:
                            raise EvaluatorException(
                                f"{err!r} in {lispstr(expr)} \n AST = {expr!r}"
                            )
                case _:
                    raise InvalidSyntax(lispstr(expr))

    def cond_form(self, clauses: list[Expression], env: Environment) -> Any:
        result = None
        for clause in clauses:
            match clause:
                case ["else", *body]:
                    for exp in body:
                        result = self.evaluate(exp, env)
                    return result
                case [test, *body] if self.evaluate(test, env):
                    for exp in body:
                        result = self.evaluate(exp, env)
                    return result

    def or_form(self, expressions: list[Expression], env: Environment) -> Any:
        value = False
        for exp in expressions:
            value = self.evaluate(exp, env)
            if value:
                return value
        return value

    def and_form(self, expressions: list[Expression], env: Environment) -> Any:
        value = True
        for exp in expressions:
            value = self.evaluate(exp, env)
            if not value:
                return value
        return value

    def interpret(self, env: Environment = standard_env()) -> Any:
        result = None
        for i in self.parser.parse():
            result = self.evaluate(i, env)
        return result


def code_exec(code: SourceCode, env: Environment = standard_env()) -> Any:
    return Interpreter(Parser(Lexer(code))).interpret(env)


def repl(prompt: str = ">>> ") -> None:
    """
    极简的repl实现
    """
    global_env: Environment = standard_env()
    while True:
        code = input(prompt)
        try:
            result = code_exec(code, global_env)
        except Exception as e:
            print(f"{e.__class__.__name__}{e}")
        else:
            if result is not None:
                print(result)


class SourceFile:
    def __init__(self, file_name: str) -> None:
        fp = open(file_name, "r", encoding="utf-8")
        self.source: SourceCode = "".join([i for i in fp.readlines()])
        fp.close()

    def lex(self) -> TokenList:
        return Lexer(self.source).lex()

    def parse(self) -> Expression:
        return Parser(Lexer(self.source)).parse()

    def interpret(self, env: Environment = standard_env()) -> Any:
        return Interpreter(Parser(Lexer(self.source))).interpret(env)


init()
