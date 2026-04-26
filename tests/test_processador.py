"""Testes de integração do processamento de arquivos Jack."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from src.processador import processar_arquivo_jack, tokenizar_arquivo_jack


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


if __name__ == "__main__":
    unittest.main()
