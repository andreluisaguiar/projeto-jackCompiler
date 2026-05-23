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


if __name__ == "__main__":
    unittest.main()
