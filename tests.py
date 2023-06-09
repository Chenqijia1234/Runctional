import unittest

from interpreter import Lexer, Parser, code_exec


class Test_Lexer(unittest.TestCase):
    def test_lexer_simple_operator(self) -> None:
        self.assertEqual(first=Lexer("(- 1 2)").lex(), second=["(", "-", "1", "2", ")"])
        self.assertEqual(first=Lexer("(+ 1 2)").lex(), second=["(", "+", "1", "2", ")"])
        self.assertEqual(first=Lexer("(* 1 2)").lex(), second=["(", "*", "1", "2", ")"])
        self.assertEqual(first=Lexer("(/ 1 2)").lex(), second=["(", "/", "1", "2", ")"])


class Test_Parser(unittest.TestCase):
    def test_parser_highest_common_divisor(self) -> None:
        self.assertEqual(
            first=Parser(
                Lexer(
                    """
(define (mod m n ) (- m (* n (quotient m n))))
(define (gcd m n) (if (= n 0) m (gcd n (mod m n))))
(display (gcd 18 45))
"""
                )
            ).parse(),
            second=[
                [
                    "define",
                    ["mod", "m", "n"],
                    ["-", "m", ["*", "n", ["quotient", "m", "n"]]],
                ],
                [
                    "define",
                    ["gcd", "m", "n"],
                    ["if", ["=", "n", 0], "m", ["gcd", "n", ["mod", "m", "n"]]],
                ],
                ["display", ["gcd", 18, 45]],
            ],
        )


class Test_Interpreter(unittest.TestCase):
    def test_interpreter_highest_common_divisor(self) -> None:
        self.assertEqual(
            first=code_exec(
                """
(define (mod m n ) (- m (* n (quotient m n))))
(define (gcd m n) (if (= n 0) m (gcd n (mod m n))))
(gcd 18 45)
        """
            ),
            second=9,
        )


def run_test() -> None:
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Test_Lexer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Test_Parser))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Test_Interpreter))

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    run_test()
