"""Testes unitários para o analisador léxico Jack"""

import unittest
from src.lexer import JackLexer, TokenType, LexerError

class TesteJackLexer(unittest.TestCase):
    """testes para a classe JackLexer"""
    
    def test_keyword(self):
        """Teste para reconhecimento de palavras-chave"""
        lexer = JackLexer("class")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].token_type, TokenType.KEYWORD)
        self.assertEqual(tokens[0].value, "class")
    
    def test_symbol(self):
        """Teste para reconhecimento de símbolos"""
        lexer = JackLexer("{ } ( )")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 4)
        self.assertTrue(all(t.token_type == TokenType.SYMBOL for t in tokens))
    
    def test_integer(self):
        """Teste para reconhecimento de números inteiros"""
        lexer = JackLexer("123 456")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "123")
        self.assertEqual(tokens[1].value, "456")
    
    def test_string(self):
        """Teste para reconhecimento de strings (valor sem aspas)"""
        lexer = JackLexer('"ola mundo"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.STRING_CONSTANT)
        self.assertEqual(tokens[0].value, "ola mundo")  # Sem aspas!
    
    def test_identifier(self):
        """Teste para reconhecimento de identificadores"""
        lexer = JackLexer("minhaVar _privado123")
        tokens = lexer.tokenize()
        self.assertTrue(all(t.token_type == TokenType.IDENTIFIER for t in tokens))
    
    def test_comment_line(self):
        """Teste para ignorar comentários de linha //"""
        lexer = JackLexer("x // isso é comentário\ny")
        tokens = lexer.tokenize()
        values = [t.value for t in tokens]
        self.assertIn("x", values)
        self.assertIn("y", values)
        self.assertNotIn("//", values)
        
    def test_comment_block(self):
        """Teste para ignorar comentários de bloco /* */"""
        lexer = JackLexer("a /* comentário\nmultilinha */ b")
        tokens = lexer.tokenize()
        values = [t.value for t in tokens]
        self.assertIn("a", values)
        self.assertIn("b", values)
        self.assertEqual(len(tokens), 2)
    
    def test_xml_escape(self):
        """Teste para escape correto de caracteres especiais no XML"""
        lexer = JackLexer('"<&>"')
        tokens = lexer.tokenize()
        xml = tokens[0].to_xml()
        self.assertIn("&lt;", xml)
        self.assertIn("&gt;", xml)
        self.assertIn("&amp;", xml)
    
    def test_integer_out_of_range(self):
        """Teste de erro para inteiro fora do intervalo 0-32767"""
        lexer = JackLexer("99999")
        with self.assertRaises(LexerError):
            lexer.tokenize()
    
    def test_unterminated_string(self):
        """Teste de erro para string não finalizada"""
        lexer = JackLexer('"string sem fim')
        with self.assertRaises(LexerError):
            lexer.tokenize()

if __name__ == "__main__":
    unittest.main()