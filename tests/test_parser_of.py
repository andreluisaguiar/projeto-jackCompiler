"""Testes do parser Jack contra arquivos XML oficiais do nand2tetris."""

import unittest
from pathlib import Path
from src.lexer import JackLexer
from src.parser import JackParser


def normalize_for_comparison(xml_content: str) -> str:
    """
    Normaliza XML para comparação estrutural (ignora indentação).
    Equivalente ao comportamento de: diff -w
    """
    lines = xml_content.split('\n')
    normalized = [line.lstrip(' \t') for line in lines if line.strip()]
    return '\n'.join(normalized)


def parse_jack_file(jack_path: str) -> str:
    """Executa lexer + parser completo e retorna XML string."""
    with open(jack_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    lexer = JackLexer(source)
    tokens = lexer.tokenize()
    
    parser = JackParser(tokens)
    return parser.parse()  # Ponto de entrada: compile_class()


class TestParserOfficialFiles(unittest.TestCase):
    """Valida saída do parser contra arquivos XML oficiais em Square/"""
    
    BASE_DIR = Path(__file__).parent.parent
    SQUARE_DIR = BASE_DIR / 'Square'
    
    def _assert_matches_official(self, jack_filename: str):
        """Helper: compara output do parser com XML oficial correspondente"""
        jack_path = self.SQUARE_DIR / jack_filename
        xml_filename = jack_filename.replace('.jack', '.xml')
        xml_path = self.SQUARE_DIR / xml_filename
        
        self.assertTrue(jack_path.exists(), f"❌ Jack não encontrado: {jack_path}")
        self.assertTrue(xml_path.exists(), f"❌ XML oficial não encontrado: {xml_path}")
        
        generated = normalize_for_comparison(parse_jack_file(str(jack_path)))
        reference = normalize_for_comparison(xml_path.read_text(encoding='utf-8'))
        
        self.assertEqual(
            generated, reference,
            f"❌ Diferença estrutural em {jack_filename}\n"
            f"💡 Execute: diff -w output/{xml_filename} {xml_path} para detalhes"
        )
    
    def test_main_official(self):
        """Valida Main.jack → Main.xml"""
        self._assert_matches_official('Main.jack')
    
    def test_square_official(self):
        """Valida Square.jack → Square.xml"""
        self._assert_matches_official('Square.jack')
    
    def test_squaregame_official(self):
        """Valida SquareGame.jack → SquareGame.xml"""
        self._assert_matches_official('SquareGame.jack')


if __name__ == '__main__':
    unittest.main(verbosity=2)