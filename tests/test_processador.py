"""Testes de integração do processamento de arquivos Jack."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from src.processador import (
    calcular_caminho_saida_vm,
    compilar_entrada,
    processar_arquivo_jack,
    resolver_arquivos_jack,
    tokenizar_arquivo_jack,
)


def normalize_xml(content: str) -> str:
    return '\n'.join(line.lstrip() for line in content.splitlines() if line.strip())


class TestProcessadorJack(unittest.TestCase):
    BASE_DIR = Path(__file__).parent.parent
    SQUARE_DIR = BASE_DIR / "Square"

    def test_processa_arquivo_jack_e_gera_xml_sintatico(self):
        with TemporaryDirectory() as temp_dir:
            saida = Path(temp_dir) / "Main.xml"

            with redirect_stdout(StringIO()):
                caminho_gerado = processar_arquivo_jack(
                    str(self.SQUARE_DIR / "Main.jack"),
                    str(saida),
                )

            self.assertEqual(caminho_gerado, str(saida))
            self.assertTrue(saida.exists())
            self.assertEqual(
                normalize_xml(saida.read_text(encoding="utf-8")),
                normalize_xml((self.SQUARE_DIR / "Main.xml").read_text(encoding="utf-8")),
            )

    def test_tokeniza_arquivo_jack_quando_solicitado(self):
        with TemporaryDirectory() as temp_dir:
            saida = Path(temp_dir) / "MainT.xml"

            with redirect_stdout(StringIO()):
                caminho_gerado = tokenizar_arquivo_jack(
                    str(self.SQUARE_DIR / "Main.jack"),
                    str(saida),
                )

            self.assertEqual(caminho_gerado, str(saida))
            conteudo = saida.read_text(encoding="utf-8")
            self.assertTrue(conteudo.startswith("<tokens>"))
            self.assertIn("<keyword> class </keyword>", conteudo)

    def test_resolve_arquivos_jack_em_diretorio_recursivo(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            sub_dir = base_dir / "sub"
            sub_dir.mkdir()
            primeiro = base_dir / "Main.jack"
            segundo = sub_dir / "Helper.jack"
            ignorado = base_dir / "notes.txt"

            primeiro.write_text("class Main {}", encoding="utf-8")
            segundo.write_text("class Helper {}", encoding="utf-8")
            ignorado.write_text("nao entra", encoding="utf-8")

            self.assertEqual(
                resolver_arquivos_jack(str(base_dir)),
                [primeiro, segundo],
            )

    def test_resolve_arquivo_jack_unico(self):
        with TemporaryDirectory() as temp_dir:
            arquivo = Path(temp_dir) / "Main.jack"
            arquivo.write_text("class Main {}", encoding="utf-8")

            self.assertEqual(resolver_arquivos_jack(str(arquivo)), [arquivo])

    def test_erro_quando_diretorio_nao_tem_jack(self):
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                resolver_arquivos_jack(temp_dir)

    def test_calcula_saida_vm_ao_lado_do_arquivo(self):
        entrada = Path("Project") / "Main.jack"

        self.assertEqual(
            calcular_caminho_saida_vm(entrada),
            Path("Project") / "Main.vm",
        )

    def test_calcula_saida_vm_preservando_estrutura_relativa(self):
        raiz = Path("Project")
        entrada = raiz / "sub" / "Helper.jack"

        self.assertEqual(
            calcular_caminho_saida_vm(entrada, raiz, "output"),
            Path("output") / "sub" / "Helper.vm",
        )

    def test_compila_entrada_diretorio_e_gera_multiplos_vm(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "Project"
            sub_dir = base_dir / "sub"
            output_dir = Path(temp_dir) / "out"
            sub_dir.mkdir(parents=True)

            (base_dir / "Main.jack").write_text(
                """
                class Main {
                   function void main() {
                      return;
                   }
                }
                """,
                encoding="utf-8",
            )
            (sub_dir / "Helper.jack").write_text(
                """
                class Helper {
                   function int value() {
                      return 1;
                   }
                }
                """,
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                caminhos = compilar_entrada(str(base_dir), output_dir)

            self.assertEqual(
                caminhos,
                [
                    str(output_dir / "Main.vm"),
                    str(output_dir / "sub" / "Helper.vm"),
                ],
            )
            self.assertTrue((output_dir / "Main.vm").exists())
            self.assertTrue((output_dir / "sub" / "Helper.vm").exists())


if __name__ == "__main__":
    unittest.main()
