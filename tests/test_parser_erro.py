"""Testes de erro sintático do parser Jack."""

import unittest
from src.lexer import JackLexer
from src.parser import JackParser, ParserError


class TestParserSyntaxErrors(unittest.TestCase):
    """Valida que o parser detecta e reporta erros sintáticos corretamente."""
    
    def _expect_parser_error(self, source: str, expected_in_message: str):
        """Helper: espera ParserError com substring na mensagem"""
        lexer = JackLexer(source)
        tokens = lexer.tokenize()
        parser = JackParser(tokens)
        
        with self.assertRaises(ParserError) as context:
            parser.parse()
        
        error_msg = str(context.exception).lower()
        self.assertIn(
            expected_in_message.lower(),
            error_msg,
            f"Erro não contém '{expected_in_message}': {context.exception}"
        )
    
    def test_class_missing_opening_brace(self):
        """Erro: declaração de classe sem '{' de abertura"""
        self._expect_parser_error(
            "class Main function void main() { return; } }",
            "Expected SYMBOL '{'"
        )
    
    def test_let_double_semicolon(self):
        """Erro: let statement com ';;' (expressão inválida)"""
        self._expect_parser_error(
            "class Main { function void main() { let x = ;; return; } }",
            "Expected"
        )
    
    def test_return_missing_semicolon(self):
        """Erro: return statement sem ';' terminador"""
        self._expect_parser_error(
            "class Main { function void main() { return 0 } }",
            "Expected SYMBOL ';'"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)