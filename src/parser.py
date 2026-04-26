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
        """Executa o parser completo a partir da regra class."""
        self.compile_class()
        if not self.is_at_end():
            token = self.peek()
            raise ParserError(
                f"Unexpected token after class: {token.value}",
                token.line,
                token.column,
            )
        return self.output()

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
        """class: 'class' className '{' classVarDec* subroutineDec* '}'"""
        self.write_start("class")

        self.consume_and_write(TokenType.KEYWORD, 'class')
        self.consume_and_write(TokenType.IDENTIFIER, description="class name")
        self.consume_and_write(TokenType.SYMBOL, '{')

        while self.check(TokenType.KEYWORD) and self.peek().value in ('static', 'field'):
            self.compile_class_var_dec()

        while self.check(TokenType.KEYWORD) and self.peek().value in ('constructor', 'function', 'method'):
            self.compile_subroutine_dec()

        self.consume_and_write(TokenType.SYMBOL, '}')
        self.write_end("class")

    def compile_class_var_dec(self):
        """classVarDec: ('static' | 'field') type varName (',' varName)* ';'"""
        self.write_start("classVarDec")

        if not (self.check(TokenType.KEYWORD, 'static') or self.check(TokenType.KEYWORD, 'field')):
            token = self.peek()
            raise ParserError("Expected class variable declaration", token.line, token.column)

        self.consume_and_write(TokenType.KEYWORD)
        self._compile_type()
        self.consume_and_write(TokenType.IDENTIFIER, description="variable name")

        while self.check(TokenType.SYMBOL, ','):
            self.consume_and_write(TokenType.SYMBOL, ',')
            self.consume_and_write(TokenType.IDENTIFIER, description="variable name")

        self.consume_and_write(TokenType.SYMBOL, ';')
        self.write_end("classVarDec")

    def compile_subroutine_dec(self):
        """subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        self.write_start("subroutineDec")

        if not self.check(TokenType.KEYWORD) or self.peek().value not in ('constructor', 'function', 'method'):
            token = self.peek()
            raise ParserError("Expected subroutine declaration", token.line, token.column)

        self.consume_and_write(TokenType.KEYWORD)
        self._compile_return_type()
        self.consume_and_write(TokenType.IDENTIFIER, description="subroutine name")
        self.consume_and_write(TokenType.SYMBOL, '(')
        self.compile_parameter_list()
        self.consume_and_write(TokenType.SYMBOL, ')')
        self.compile_subroutine_body()

        self.write_end("subroutineDec")

    def compile_parameter_list(self):
        """parameterList: ((type varName) (',' type varName)*)?"""
        self.write_start("parameterList")

        if not self.check(TokenType.SYMBOL, ')'):
            self._compile_type()
            self.consume_and_write(TokenType.IDENTIFIER, description="parameter name")

            while self.check(TokenType.SYMBOL, ','):
                self.consume_and_write(TokenType.SYMBOL, ',')
                self._compile_type()
                self.consume_and_write(TokenType.IDENTIFIER, description="parameter name")

        self.write_end("parameterList")

    def compile_subroutine_body(self):
        """subroutineBody: '{' varDec* statements '}'"""
        self.write_start("subroutineBody")

        self.consume_and_write(TokenType.SYMBOL, '{')

        while self.check(TokenType.KEYWORD, 'var'):
            self.compile_var_dec()

        self.compile_statements()
        self.consume_and_write(TokenType.SYMBOL, '}')

        self.write_end("subroutineBody")

    def compile_var_dec(self):
        """varDec: 'var' type varName (',' varName)* ';'"""
        self.write_start("varDec")

        self.consume_and_write(TokenType.KEYWORD, 'var')
        self._compile_type()
        self.consume_and_write(TokenType.IDENTIFIER, description="variable name")

        while self.check(TokenType.SYMBOL, ','):
            self.consume_and_write(TokenType.SYMBOL, ',')
            self.consume_and_write(TokenType.IDENTIFIER, description="variable name")

        self.consume_and_write(TokenType.SYMBOL, ';')
        self.write_end("varDec")

    def _compile_type(self):
        if self.check(TokenType.KEYWORD) and self.peek().value in ('int', 'char', 'boolean'):
            self.consume_and_write(TokenType.KEYWORD)
        elif self.check(TokenType.IDENTIFIER):
            self.consume_and_write(TokenType.IDENTIFIER, description="class name")
        else:
            token = self.peek()
            if token is None:
                line, column = self._eof_position()
                raise ParserError("Expected type, found end of input", line, column)
            raise ParserError(f"Expected type, found {token.value}", token.line, token.column)

    def _compile_return_type(self):
        if self.check(TokenType.KEYWORD, 'void'):
            self.consume_and_write(TokenType.KEYWORD, 'void')
        else:
            self._compile_type()

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

    def compile_expression(self):
        """expression: term (op term)*
        Binary ops: + - * / & | < > = (all same precedence in Jack)
        """
        self.compile_term()
        
        while self.check(TokenType.SYMBOL) and self.peek().value in '+-*/&|<=>':
            op_token = self.advance()
            self.write_token(op_token) 
            self.compile_term()

    def compile_let(self):
        """letStatement: 'let' varName ('[' expression ']')? '=' expression ';'"""
        self.write_start("letStatement")
        
        self.consume_and_write(TokenType.KEYWORD, 'let')
        self.consume_and_write(TokenType.IDENTIFIER, description="variable name")
        
        if self.check(TokenType.SYMBOL, '['):
            self.consume_and_write(TokenType.SYMBOL, '[')
            self.write_start("expression")
            self.compile_expression()  
            self.write_end("expression")
            self.consume_and_write(TokenType.SYMBOL, ']')
 
        self.consume_and_write(TokenType.SYMBOL, '=')
        self.write_start("expression")
        self.compile_expression()
        self.write_end("expression")
        self.consume_and_write(TokenType.SYMBOL, ';')
        self.write_end("letStatement")

    def compile_if(self):
        """ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        self.write_start("ifStatement")
        
        self.consume_and_write(TokenType.KEYWORD, 'if')
        self.consume_and_write(TokenType.SYMBOL, '(')
        
        self.write_start("expression")
        self.compile_expression() 
        self.write_end("expression")
        
        self.consume_and_write(TokenType.SYMBOL, ')')
        self.consume_and_write(TokenType.SYMBOL, '{')
        self.compile_statements()
        self.consume_and_write(TokenType.SYMBOL, '}')
        
        if self.check(TokenType.KEYWORD, 'else'):
            self.consume_and_write(TokenType.KEYWORD, 'else')
            self.consume_and_write(TokenType.SYMBOL, '{')
            self.compile_statements()
            self.consume_and_write(TokenType.SYMBOL, '}')
        
        self.write_end("ifStatement")

    def compile_while(self):
        """whileStatement: 'while' '(' expression ')' '{' statements '}'"""
        self.write_start("whileStatement")
        
        self.consume_and_write(TokenType.KEYWORD, 'while')
        self.consume_and_write(TokenType.SYMBOL, '(')
        
        self.write_start("expression")
        self.compile_expression()
        self.write_end("expression")
        
        self.consume_and_write(TokenType.SYMBOL, ')')
        self.consume_and_write(TokenType.SYMBOL, '{')
        self.compile_statements()
        self.consume_and_write(TokenType.SYMBOL, '}')
        
        self.write_end("whileStatement")
    def compile_do(self):
        """doStatement: 'do' subroutineCall ';'"""
        self.write_start("doStatement")
        
        self.consume_and_write(TokenType.KEYWORD, 'do')
        self._compile_subroutine_call()
        self.consume_and_write(TokenType.SYMBOL, ';')
        
        self.write_end("doStatement")

    def _compile_subroutine_call(self):
        """Helper: subroutineCall: identifier ('.' identifier)? '(' expressionList ')'"""

        self.consume_and_write(TokenType.IDENTIFIER)
     
        if self.check(TokenType.SYMBOL, '.'):
            self.consume_and_write(TokenType.SYMBOL, '.')
            self.consume_and_write(TokenType.IDENTIFIER, description="subroutine name")
        
        self.consume_and_write(TokenType.SYMBOL, '(')
        self.compile_expression_list()  
        self.consume_and_write(TokenType.SYMBOL, ')')

    def compile_return(self):
        """returnStatement: 'return' expression? ';'"""
        self.write_start("returnStatement")
        
        self.consume_and_write(TokenType.KEYWORD, 'return')
        
        if not self.check(TokenType.SYMBOL, ';'):
            self.write_start("expression")
            self.compile_expression()
            self.write_end("expression")
        
        self.consume_and_write(TokenType.SYMBOL, ';')
        
        self.write_end("returnStatement")

    def compile_term(self):
        """term: integerConstant | stringConstant | keywordConstant | 
                 varName | varName '[' expression ']' | 
                 subroutineCall | '(' expression ')' | unaryOp term
        """
        self.write_start("term")
        
        token = self.peek()
        if token is None:
            raise ParserError("Expected term, found end of input", 
                            *self._eof_position())
        
        if self.check(TokenType.SYMBOL, '-') or self.check(TokenType.SYMBOL, '~'):
            self.consume_and_write(TokenType.SYMBOL)
            self.compile_term()
            
        elif self.check(TokenType.SYMBOL, '('):
            self.consume_and_write(TokenType.SYMBOL, '(')
            self.write_start("expression")
            self.compile_expression()
            self.write_end("expression")
            self.consume_and_write(TokenType.SYMBOL, ')')
            
        elif self.check(TokenType.INTEGER_CONSTANT):
            self.consume_and_write(TokenType.INTEGER_CONSTANT)
        elif self.check(TokenType.STRING_CONSTANT):
            self.consume_and_write(TokenType.STRING_CONSTANT)
        elif self.check(TokenType.KEYWORD) and token.value in ('true', 'false', 'null', 'this'):
            self.consume_and_write(TokenType.KEYWORD)
        
        elif self.check(TokenType.IDENTIFIER):
            identifier = self.advance()
            self.write_token(identifier)
            
            if self.check(TokenType.SYMBOL, '['):
                self.consume_and_write(TokenType.SYMBOL, '[')
                self.write_start("expression")
                self.compile_expression()
                self.write_end("expression")
                self.consume_and_write(TokenType.SYMBOL, ']')
            
            elif self.check(TokenType.SYMBOL, '(') or self.check(TokenType.SYMBOL, '.'):
                if self.check(TokenType.SYMBOL, '.'):
                    self.consume_and_write(TokenType.SYMBOL, '.')
                    self.consume_and_write(TokenType.IDENTIFIER, description="subroutine name")
                self.consume_and_write(TokenType.SYMBOL, '(')
                self.compile_expression_list()
                self.consume_and_write(TokenType.SYMBOL, ')')
                
        else:
            raise ParserError(f"Unexpected token in term: {token.value}", 
                            token.line, token.column)
        
        self.write_end("term")

    def compile_expression_list(self):
        """expressionList: (expression (',' expression)*)?"""
        self.write_start("expressionList")
        
        if not self.check(TokenType.SYMBOL, ')'):
            self.write_start("expression")
            self.compile_expression()
            self.write_end("expression")
            
            while self.check(TokenType.SYMBOL, ','):
                self.consume_and_write(TokenType.SYMBOL, ',')
                self.write_start("expression")
                self.compile_expression()
                self.write_end("expression")
        
        self.write_end("expressionList")
