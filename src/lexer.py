# Analizador lexico para a linguagem Jack
# Compiladores | Unidade 1

from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    SYMBOL = auto()
    INTEGER_CONSTANT = auto()
    STRING_CONSTANT = auto()
    IDENTIFIER = auto()


TAG_NAME = {
    TokenType.KEYWORD: 'keyword',
    TokenType.SYMBOL: 'symbol',
    TokenType.INTEGER_CONSTANT: 'integerConstant',
    TokenType.STRING_CONSTANT: 'stringConstant',
    TokenType.IDENTIFIER: 'identifier',
}

XML_ESCAPE = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
}

KEYWORDS = {
    'class', 'constructor', 'function', 'method', 'field', 'static',
    'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
    'this', 'let', 'do', 'if', 'else', 'while', 'return'
}

SYMBOLS = set('{}()[].,;+-*/&|<>=~')



class Token:
    def __init__(self, token_type: TokenType, value: str, line: int = 1, column: int = 1):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.token_type.name}, {self.value!r}, line={self.line}, column={self.column})"
    
    def to_xml(self) -> str:
        tag = TAG_NAME[self.token_type]
        escaped = self._escape(self.value)
        return f"<{tag}> {escaped} </{tag}>"

    def _escape(self, text: str) -> str:
        result = []
        for ch in text:
            result.append(XML_ESCAPE.get(ch, ch))
        return ''.join(result)
  
class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int = 1):
        super().__init__(f"Line {line}, column {column}: {message}")
        self.line = line
        self.column = column

class JackLexer:
    def __init__(self, source: str):
        self._source = source
        self._pos = 0
        self._line = 1
        self._column = 1
        self._tokens: list[Token] = []

    def _advance_char(self) -> str:
        ch = self._source[self._pos]
        self._pos += 1
        if ch == '\n':
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return ch

    def _read_word(self):
        line = self._line
        column = self._column
        start = self._pos
        while self._pos < len(self._source) and (
            self._source[self._pos].isalnum() or self._source[self._pos] == '_'
        ):
            self._advance_char()
        word = self._source[start:self._pos]
        if word in KEYWORDS:
            self._tokens.append(Token(TokenType.KEYWORD, word, line, column))
        else:
            self._tokens.append(Token(TokenType.IDENTIFIER, word, line, column))

    def _read_symbol(self):
        line = self._line
        column = self._column
        ch = self._advance_char()
        self._tokens.append(Token(TokenType.SYMBOL, ch, line, column))
        
    def _read_integer(self):
        line = self._line
        column = self._column
        start = self._pos
        while self._pos < len(self._source) and self._source[self._pos].isdigit():
            self._advance_char()
        value = self._source[start:self._pos]
        int_val = int(value)
        if not (0 <= int_val <= 32767):
            raise LexerError(f"Integer {int_val} out of range [0, 32767]", line, column)
        self._tokens.append(Token(TokenType.INTEGER_CONSTANT, value, line, column))

    def _read_string(self):
        line = self._line
        column = self._column
        self._advance_char()  # pula a aspas de abertura "
        start = self._pos
        while self._pos < len(self._source) and self._source[self._pos] != '"':
            if self._source[self._pos] == '\n':
                raise LexerError("Newline inside string literal", self._line, self._column)
            self._advance_char()
        if self._pos >= len(self._source):
            raise LexerError("Unterminated string literal", line, column)
        value = self._source[start:self._pos]
        self._advance_char()  # pula a aspas de fechamento "
        self._tokens.append(Token(TokenType.STRING_CONSTANT, value, line, column))

    def _skip_whitespace_and_comments(self):
        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch in ' \t\r\n':
                self._advance_char()
                continue
            if ch == '/' and self._pos + 1 < len(self._source) and self._source[self._pos + 1] == '/':
                while self._pos < len(self._source) and self._source[self._pos] != '\n':
                    self._advance_char()
                continue
            if ch == '/' and self._pos + 1 < len(self._source) and self._source[self._pos + 1] == '*':
                start_line = self._line
                start_column = self._column
                self._advance_char()
                self._advance_char()
                while self._pos + 1 < len(self._source):
                    if self._source[self._pos] == '*' and self._source[self._pos + 1] == '/':
                        self._advance_char()
                        self._advance_char()
                        break
                    self._advance_char()
                else:
                    raise LexerError("Unterminated block comment", start_line, start_column)
                continue
            break

    def _read_next_token(self):
        self._skip_whitespace_and_comments()
        if self._pos >= len(self._source):
            return False
        ch = self._source[self._pos]
        if ch == '"':
            self._read_string()
        elif ch.isdigit():
            self._read_integer()
        elif ch in SYMBOLS:
            self._read_symbol()
        elif ch.isalpha() or ch == '_':
            self._read_word()
        else:
            raise LexerError(f"Unexpected character: {ch!r}", self._line, self._column)
        return True

    def tokenize(self) -> list[Token]:
        while self._read_next_token():
            pass
        return self._tokens

    def to_xml(self) -> str:
        lines = ['<tokens>']
        for token in self._tokens:
            lines.append(token.to_xml())
        lines.append('</tokens>')
        return '\n'.join(lines)    
