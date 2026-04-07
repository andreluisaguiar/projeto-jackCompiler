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
    def __init__(self, token_type: TokenType, value: str):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_type.name}, {self.value!r})"
    
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
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line

class JackLexer:
    def __init__(self, source: str):
        self._source = source
        self._pos = 0
        self._line = 1
        self._tokens: list[Token] = []

    def _skip_whitespace(self):
        while self._pos < len(self._source) and self._source[self._pos] in ' \t\r\n':
            if self._source[self._pos] == '\n':
                self._line += 1
            self._pos += 1

    def _read_word(self):
        start = self._pos
        while self._pos < len(self._source) and (
            self._source[self._pos].isalnum() or self._source[self._pos] == '_'
        ):
            self._pos += 1
        word = self._source[start:self._pos]
        if word in KEYWORDS:
            self._tokens.append(Token(TokenType.KEYWORD, word))
        else:
            self._tokens.append(Token(TokenType.IDENTIFIER, word))

    def _read_symbol(self):
        ch = self._source[self._pos]
        self._tokens.append(Token(TokenType.SYMBOL, ch))
        self._pos += 1
        
    def _read_integer(self):
        start = self._pos
        while self._pos < len(self._source) and self._source[self._pos].isdigit():
            self._pos += 1
        value = self._source[start:self._pos]
        int_val = int(value)
        if not (0 <= int_val <= 32767):
            raise LexerError(f"Integer {int_val} out of range [0, 32767]", self._line)
        self._tokens.append(Token(TokenType.INTEGER_CONSTANT, value))

    def _read_string(self):
        self._pos += 1  # pula a aspas de abertura "
        start = self._pos
        while self._pos < len(self._source) and self._source[self._pos] != '"':
            if self._source[self._pos] == '\n':
                raise LexerError("Newline inside string literal", self._line)
            self._pos += 1
        if self._pos >= len(self._source):
            raise LexerError("Unterminated string literal", self._line)
        value = self._source[start:self._pos]
        self._pos += 1  # pula a aspas de fechamento "
        self._tokens.append(Token(TokenType.STRING_CONSTANT, value))

    def _read_next_token(self):
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
            raise LexerError(f"Unexpected character: {ch!r}", self._line)

    def _skip_whitespace_and_comments(self):
        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch in ' \t\r\n':
                if ch == '\n': self._line += 1
                self._pos += 1
                continue
            if ch == '/' and self._pos + 1 < len(self._source) and self._source[self._pos + 1] == '/':
                while self._pos < len(self._source) and self._source[self._pos] != '\n':
                    self._pos += 1
                continue
            if ch == '/' and self._pos + 1 < len(self._source) and self._source[self._pos + 1] == '*':
                self._pos += 2
                while self._pos + 1 < len(self._source):
                    if self._source[self._pos] == '*' and self._source[self._pos + 1] == '/':
                        self._pos += 2
                        break
                    if self._source[self._pos] == '\n': self._line += 1
                    self._pos += 1
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
            raise LexerError(f"Unexpected character: {ch!r}", self._line)
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