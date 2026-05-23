"""Testes do escritor de comandos VM."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.vm_writer import VMWriter


class TestVMWriter(unittest.TestCase):
    def test_escreve_comandos_vm_basicos(self):
        writer = VMWriter()

        writer.write_push("constant", 5)
        writer.write_pop("local", 1)
        writer.write_arithmetic("add")
        writer.write_label("LOOP")
        writer.write_goto("LOOP")
        writer.write_if("END")
        writer.write_call("Math.abs", 1)
        writer.write_function("Main.main", 2)
        writer.write_return()

        self.assertEqual(
            writer.output(),
            "\n".join(
                [
                    "push constant 5",
                    "pop local 1",
                    "add",
                    "label LOOP",
                    "goto LOOP",
                    "if-goto END",
                    "call Math.abs 1",
                    "function Main.main 2",
                    "return",
                ]
            ),
        )

    def test_rejeita_segmento_invalido(self):
        writer = VMWriter()

        with self.assertRaises(ValueError):
            writer.write_push("invalid", 0)

    def test_rejeita_pop_constant(self):
        writer = VMWriter()

        with self.assertRaises(ValueError):
            writer.write_pop("constant", 0)

    def test_rejeita_comando_aritmetico_invalido(self):
        writer = VMWriter()

        with self.assertRaises(ValueError):
            writer.write_arithmetic("multiply")

    def test_rejeita_nome_vazio(self):
        writer = VMWriter()

        with self.assertRaises(ValueError):
            writer.write_label("")

    def test_salva_arquivo_vm(self):
        writer = VMWriter()
        writer.write_push("constant", 7)

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "Main.vm"
            writer.save(output_path)

            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "push constant 7\n",
            )


if __name__ == "__main__":
    unittest.main()
