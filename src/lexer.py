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
        self._source = source  # strip de comentários virá depois
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

    SYMBOLS = set('{}()[].,;+-*/&|<>=~')

    def _read_symbol(self):
        ch = self._source[self._pos]
        self._tokens.append(Token(TokenType.SYMBOL, ch))
        self._pos += 1

    def _read_next_token(self):
        ch = self._source[self._pos]
        if ch in SYMBOLS:
            self._read_symbol()
        elif ch.isalpha() or ch == '_':
            self._read_word()