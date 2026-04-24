"""Testes da infraestrutura inicial do parser Jack."""

import unittest

from src.lexer import JackLexer, Token, TokenType
from src.parser import JackParser, ParserError


class TesteParserHelpers(unittest.TestCase):
    def test_tokens_guardam_linha_e_coluna(self):
        lexer = JackLexer("class Main {\n  function void main() {}\n}")
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].value, "class")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)
        self.assertEqual(tokens[3].value, "function")
        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].column, 3)

    def test_peek_advance_match_e_consume(self):
        tokens = [
            Token(TokenType.KEYWORD, "class", 4, 2),
            Token(TokenType.IDENTIFIER, "Main", 4, 8),
        ]
        parser = JackParser(tokens)

        self.assertEqual(parser.peek().value, "class")
        self.assertTrue(parser.match(TokenType.KEYWORD, "class"))
        identifier = parser.consume(TokenType.IDENTIFIER)
        self.assertEqual(identifier.value, "Main")
        self.assertTrue(parser.is_at_end())

    def test_consume_informa_linha_e_coluna_no_erro(self):
        parser = JackParser([Token(TokenType.IDENTIFIER, "Main", 7, 5)])

        with self.assertRaises(ParserError) as context:
            parser.consume(TokenType.KEYWORD, "class")

        self.assertEqual(context.exception.line, 7)
        self.assertEqual(context.exception.column, 5)
        self.assertIn("Expected KEYWORD 'class'", str(context.exception))

    def test_consume_and_write_gera_xml_indentado(self):
        parser = JackParser([Token(TokenType.KEYWORD, "class", 1, 1)])

        parser.write_start("class")
        parser.consume_and_write(TokenType.KEYWORD, "class")
        parser.write_end("class")

        self.assertEqual(
            parser.output(),
            "<class>\n  <keyword> class </keyword>\n</class>",
        )


if __name__ == "__main__":
    unittest.main()
