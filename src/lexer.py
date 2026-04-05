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