"""Testes da geracao de codigo VM."""

import unittest

from src.vm_compiler import compilar_codigo_jack


class TestJackVMCompiler(unittest.TestCase):
    def test_compila_subrotina_void_com_do_e_return(self):
        codigo = """
        class Main {
           function void main() {
              do Output.printInt(1);
              return;
           }
        }
        """

        self.assertEqual(
            compilar_codigo_jack(codigo),
            "\n".join(
                [
                    "function Main.main 0",
                    "push constant 1",
                    "call Output.printInt 1",
                    "pop temp 0",
                    "push constant 0",
                    "return",
                ]
            ),
        )

    def test_compila_return_com_expressao_simples(self):
        codigo = """
        class Main {
           function int value() {
              return 2 + 3;
           }
        }
        """

        self.assertEqual(
            compilar_codigo_jack(codigo),
            "\n".join(
                [
                    "function Main.value 0",
                    "push constant 2",
                    "push constant 3",
                    "add",
                    "return",
                ]
            ),
        )

    def test_compila_let_com_argumentos_e_variavel_local(self):
        codigo = """
        class Main {
           function int sum(int a, int b) {
              var int c;
              let c = a + b;
              return c;
           }
        }
        """

        self.assertEqual(
            compilar_codigo_jack(codigo),
            "\n".join(
                [
                    "function Main.sum 1",
                    "push argument 0",
                    "push argument 1",
                    "add",
                    "pop local 0",
                    "push local 0",
                    "return",
                ]
            ),
        )

    def test_compila_while_e_if_else_com_labels_previsiveis(self):
        codigo = """
        class Main {
           function void main() {
              var int i;
              let i = 0;
              while (i < 2) {
                 if (i = 1) {
                    do Output.printInt(i);
                 } else {
                    do Output.printInt(0);
                 }
                 let i = i + 1;
              }
              return;
           }
        }
        """

        self.assertEqual(
            compilar_codigo_jack(codigo),
            "\n".join(
                [
                    "function Main.main 1",
                    "push constant 0",
                    "pop local 0",
                    "label WHILE_EXP0",
                    "push local 0",
                    "push constant 2",
                    "lt",
                    "not",
                    "if-goto WHILE_END0",
                    "push local 0",
                    "push constant 1",
                    "eq",
                    "if-goto IF_TRUE0",
                    "goto IF_FALSE0",
                    "label IF_TRUE0",
                    "push local 0",
                    "call Output.printInt 1",
                    "pop temp 0",
                    "goto IF_END0",
                    "label IF_FALSE0",
                    "push constant 0",
                    "call Output.printInt 1",
                    "pop temp 0",
                    "label IF_END0",
                    "push local 0",
                    "push constant 1",
                    "add",
                    "pop local 0",
                    "goto WHILE_EXP0",
                    "label WHILE_END0",
                    "push constant 0",
                    "return",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
