"""Esqueleto do parser recursive descent para a linguagem Jack."""

from src.lexer import Token, TokenType


class ParserError(Exception):
    """Erro sintático com posição do token que causou a falha."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Line {line}, column {column}: {message}")
        self.line = line
        self.column = column


class JackParser:
    """Base do analisador sintático Jack.

    Esta classe concentra os helpers de navegação/consumo de tokens e a
    escrita XML indentada. As regras da gramática serão implementadas nos
    métodos compile_* usando recursive descent.
    """

    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0
        self._lines: list[str] = []
        self._indent = 0

    def parse(self) -> str:
        """Ponto de entrada futuro do parser completo."""
        return self.compile_class()

    def peek(self, offset: int = 0) -> Token | None:
        """Retorna o token atual sem consumir."""
        index = self._current + offset
        if index >= len(self._tokens):
            return None
        return self._tokens[index]

    def previous(self) -> Token | None:
        """Retorna o ultimo token consumido."""
        if self._current == 0:
            return None
        return self._tokens[self._current - 1]

    def is_at_end(self) -> bool:
        return self._current >= len(self._tokens)

    def advance(self) -> Token:
        """Consome e retorna o token atual."""
        if self.is_at_end():
            line, column = self._eof_position()
            raise ParserError("Unexpected end of input", line, column)

        token = self._tokens[self._current]
        self._current += 1
        return token

    def check(self, token_type: TokenType, value: str | None = None, offset: int = 0) -> bool:
        """Verifica se o token apontado combina com tipo e valor esperado."""
        token = self.peek(offset)
        if token is None or token.token_type != token_type:
            return False
        return value is None or token.value == value

    def match(self, token_type: TokenType, value: str | None = None) -> bool:
        """Consome o token atual se ele combinar com tipo e valor."""
        if not self.check(token_type, value):
            return False
        self.advance()
        return True

    def consume(self, token_type: TokenType, value: str | None = None, description: str | None = None) -> Token:
        """Consome um token obrigatório ou lança ParserError."""
        if self.check(token_type, value):
            return self.advance()

        token = self.peek()
        expected = description or self._describe_expected(token_type, value)
        if token is None:
            line, column = self._eof_position()
            found = "end of input"
        else:
            line, column = token.line, token.column
            found = f"{token.token_type.name} {token.value!r}"

        raise ParserError(f"Expected {expected}, found {found}", line, column)

    def write_start(self, tag: str):
        self._write_line(f"<{tag}>")
        self._indent += 1

    def write_end(self, tag: str):
        self._indent -= 1
        self._write_line(f"</{tag}>")

    def write_token(self, token: Token):
        self._write_line(token.to_xml())

    def consume_and_write(
        self,
        token_type: TokenType,
        value: str | None = None,
        description: str | None = None,
    ) -> Token:
        token = self.consume(token_type, value, description)
        self.write_token(token)
        return token

    def output(self) -> str:
        return "\n".join(self._lines)

    def compile_class(self) -> str:
        raise NotImplementedError("compile_class sera implementado na proxima etapa")

    def compile_class_var_dec(self):
        raise NotImplementedError("compile_class_var_dec sera implementado na proxima etapa")

    def compile_subroutine_dec(self):
        raise NotImplementedError("compile_subroutine_dec sera implementado na proxima etapa")

    def compile_parameter_list(self):
        raise NotImplementedError("compile_parameter_list sera implementado na proxima etapa")

    def compile_subroutine_body(self):
        raise NotImplementedError("compile_subroutine_body sera implementado na proxima etapa")

    def compile_var_dec(self):
        raise NotImplementedError("compile_var_dec sera implementado na proxima etapa")

    def _write_line(self, line: str):
        self._lines.append("  " * self._indent + line)

    def _eof_position(self) -> tuple[int, int]:
        previous = self.previous()
        if previous is None:
            return 1, 1
        return previous.line, previous.column + len(previous.value)

    def _describe_expected(self, token_type: TokenType, value: str | None) -> str:
        if value is None:
            return token_type.name
        return f"{token_type.name} {value!r}"

    def compile_statements(self):
        """statements: statement*
        statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        self.write_start("statements")
        
        while not self.is_at_end():
            if self.check(TokenType.SYMBOL, '}'):
                break
            if self.check(TokenType.SYMBOL, ')'):  
                break
   
            if self.check(TokenType.KEYWORD, 'let'):
                self.compile_let()
            elif self.check(TokenType.KEYWORD, 'if'):
                self.compile_if()
            elif self.check(TokenType.KEYWORD, 'while'):
                self.compile_while()
            elif self.check(TokenType.KEYWORD, 'do'):
                self.compile_do()
            elif self.check(TokenType.KEYWORD, 'return'):
                self.compile_return()
            else:
                break
        
        self.write_end("statements")    
