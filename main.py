from interpreter import repl, code_exec


def main() -> None:
    while True:
        c = input(
            """
Runctional v0.0.1 DEV_1_patch_1 
    1. 启动repl
    2. 运行测试
    3. 运行例子（求18与45的最小公因数）
    4. 查看文档（暂缺）
type>>>"""
        )
        if c == "1":
            repl()
        elif c == "2":
            raise NotImplementedError()
        elif c == "3":
            print(
                f"""源码：{
                '''
                (define (mod m n ) (- m (* n (quotient m n))))
                (define (gcd m n) (if (= n 0) m (gcd n (mod m n))))
                (gcd 18 45)
                '''}"""
            )
            print(
                f'''运行结果:{code_exec(
                    """
                    (define (mod m n ) (- m (* n (quotient m n))))
                    (define (gcd m n) (if (= n 0) m (gcd n (mod m n))))
                    (gcd 18 45)
                    """
                )}'''
            )
        elif c == "4":
            print("暂缺。")
        else:
            print("无效选择。")


if __name__ == "__main__":
    main()
