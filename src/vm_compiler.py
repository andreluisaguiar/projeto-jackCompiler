"""Compilation engine que traduz Jack para codigo VM."""

from dataclasses import dataclass

from src.lexer import JackLexer, Token, TokenType
from src.parser import ParserError
from src.vm_writer import VMWriter


@dataclass
class Symbol:
    type: str
    kind: str
    index: int


class JackVMCompiler:
    """Compilador Jack -> VM com tabela de simbolos interna minima."""

    KIND_TO_SEGMENT = {
        "static": "static",
        "field": "this",
        "arg": "argument",
        "var": "local",
    }

    BINARY_OPERATIONS = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq",
    }

    UNARY_OPERATIONS = {
        "-": "neg",
        "~": "not",
    }

    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0
        self._writer = VMWriter()
        self._class_name = ""
        self._class_scope: dict[str, Symbol] = {}
        self._subroutine_scope: dict[str, Symbol] = {}
        self._class_counts = {"static": 0, "field": 0}
        self._subroutine_counts = {"arg": 0, "var": 0}
        self._label_counts: dict[str, int] = {}
        self._current_subroutine_kind = ""

    def compile(self) -> str:
        self.compile_class()
        if not self.is_at_end():
            token = self.peek()
            raise ParserError(
                f"Unexpected token after class: {token.value}",
                token.line,
                token.column,
            )
        return self._writer.output()

    def peek(self, offset: int = 0) -> Token | None:
        index = self._current + offset
        if index >= len(self._tokens):
            return None
        return self._tokens[index]

    def previous(self) -> Token | None:
        if self._current == 0:
            return None
        return self._tokens[self._current - 1]

    def is_at_end(self) -> bool:
        return self._current >= len(self._tokens)

    def advance(self) -> Token:
        if self.is_at_end():
            line, column = self._eof_position()
            raise ParserError("Unexpected end of input", line, column)

        token = self._tokens[self._current]
        self._current += 1
        return token

    def check(self, token_type: TokenType, value: str | None = None, offset: int = 0) -> bool:
        token = self.peek(offset)
        if token is None or token.token_type != token_type:
            return False
        return value is None or token.value == value

    def match(self, token_type: TokenType, value: str | None = None) -> bool:
        if not self.check(token_type, value):
            return False
        self.advance()
        return True

    def consume(
        self,
        token_type: TokenType,
        value: str | None = None,
        description: str | None = None,
    ) -> Token:
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

    def compile_class(self):
        self.consume(TokenType.KEYWORD, "class")
        self._class_name = self.consume(
            TokenType.IDENTIFIER,
            description="class name",
        ).value
        self.consume(TokenType.SYMBOL, "{")

        while self.check(TokenType.KEYWORD) and self.peek().value in ("static", "field"):
            self.compile_class_var_dec()

        while self.check(TokenType.KEYWORD) and self.peek().value in (
            "constructor",
            "function",
            "method",
        ):
            self.compile_subroutine_dec()

        self.consume(TokenType.SYMBOL, "}")

    def compile_class_var_dec(self):
        kind = self.advance().value
        type_name = self._compile_type()
        self._define(self.consume(TokenType.IDENTIFIER, description="variable name").value, type_name, kind)

        while self.match(TokenType.SYMBOL, ","):
            name = self.consume(TokenType.IDENTIFIER, description="variable name").value
            self._define(name, type_name, kind)

        self.consume(TokenType.SYMBOL, ";")

    def compile_subroutine_dec(self):
        subroutine_kind = self.advance().value
        self._start_subroutine(subroutine_kind)

        if subroutine_kind == "method":
            self._define("this", self._class_name, "arg")

        self._compile_return_type()
        subroutine_name = self.consume(
            TokenType.IDENTIFIER,
            description="subroutine name",
        ).value
        self.consume(TokenType.SYMBOL, "(")
        self.compile_parameter_list()
        self.consume(TokenType.SYMBOL, ")")
        self.compile_subroutine_body(subroutine_kind, subroutine_name)

    def compile_parameter_list(self):
        if self.check(TokenType.SYMBOL, ")"):
            return

        type_name = self._compile_type()
        name = self.consume(TokenType.IDENTIFIER, description="parameter name").value
        self._define(name, type_name, "arg")

        while self.match(TokenType.SYMBOL, ","):
            type_name = self._compile_type()
            name = self.consume(TokenType.IDENTIFIER, description="parameter name").value
            self._define(name, type_name, "arg")

    def compile_subroutine_body(self, subroutine_kind: str, subroutine_name: str):
        self.consume(TokenType.SYMBOL, "{")

        while self.check(TokenType.KEYWORD, "var"):
            self.compile_var_dec()

        function_name = f"{self._class_name}.{subroutine_name}"
        self._writer.write_function(function_name, self._subroutine_counts["var"])

        if subroutine_kind == "constructor":
            self._writer.write_push("constant", self._class_counts["field"])
            self._writer.write_call("Memory.alloc", 1)
            self._writer.write_pop("pointer", 0)
        elif subroutine_kind == "method":
            self._writer.write_push("argument", 0)
            self._writer.write_pop("pointer", 0)

        self.compile_statements()
        self.consume(TokenType.SYMBOL, "}")

    def compile_var_dec(self):
        self.consume(TokenType.KEYWORD, "var")
        type_name = self._compile_type()
        name = self.consume(TokenType.IDENTIFIER, description="variable name").value
        self._define(name, type_name, "var")

        while self.match(TokenType.SYMBOL, ","):
            name = self.consume(TokenType.IDENTIFIER, description="variable name").value
            self._define(name, type_name, "var")

        self.consume(TokenType.SYMBOL, ";")

    def compile_statements(self):
        while self.check(TokenType.KEYWORD) and self.peek().value in (
            "let",
            "if",
            "while",
            "do",
            "return",
        ):
            keyword = self.peek().value
            if keyword == "let":
                self.compile_let()
            elif keyword == "if":
                self.compile_if()
            elif keyword == "while":
                self.compile_while()
            elif keyword == "do":
                self.compile_do()
            elif keyword == "return":
                self.compile_return()

    def compile_let(self):
        self.consume(TokenType.KEYWORD, "let")
        name = self.consume(TokenType.IDENTIFIER, description="variable name").value
        is_array = self.match(TokenType.SYMBOL, "[")

        if is_array:
            self._write_push_symbol(name)
            self.compile_expression()
            self.consume(TokenType.SYMBOL, "]")
            self._writer.write_arithmetic("add")

        self.consume(TokenType.SYMBOL, "=")
        self.compile_expression()
        self.consume(TokenType.SYMBOL, ";")

        if is_array:
            self._writer.write_pop("temp", 0)
            self._writer.write_pop("pointer", 1)
            self._writer.write_push("temp", 0)
            self._writer.write_pop("that", 0)
        else:
            self._write_pop_symbol(name)

    def compile_if(self):
        index = self._next_label_index("IF")
        true_label = f"IF_TRUE{index}"
        false_label = f"IF_FALSE{index}"
        end_label = f"IF_END{index}"

        self.consume(TokenType.KEYWORD, "if")
        self.consume(TokenType.SYMBOL, "(")
        self.compile_expression()
        self.consume(TokenType.SYMBOL, ")")

        self._writer.write_if(true_label)
        self._writer.write_goto(false_label)
        self._writer.write_label(true_label)

        self.consume(TokenType.SYMBOL, "{")
        self.compile_statements()
        self.consume(TokenType.SYMBOL, "}")

        if self.match(TokenType.KEYWORD, "else"):
            self._writer.write_goto(end_label)
            self._writer.write_label(false_label)
            self.consume(TokenType.SYMBOL, "{")
            self.compile_statements()
            self.consume(TokenType.SYMBOL, "}")
            self._writer.write_label(end_label)
        else:
            self._writer.write_label(false_label)

    def compile_while(self):
        index = self._next_label_index("WHILE")
        expression_label = f"WHILE_EXP{index}"
        end_label = f"WHILE_END{index}"

        self.consume(TokenType.KEYWORD, "while")
        self._writer.write_label(expression_label)
        self.consume(TokenType.SYMBOL, "(")
        self.compile_expression()
        self.consume(TokenType.SYMBOL, ")")
        self._writer.write_arithmetic("not")
        self._writer.write_if(end_label)

        self.consume(TokenType.SYMBOL, "{")
        self.compile_statements()
        self.consume(TokenType.SYMBOL, "}")
        self._writer.write_goto(expression_label)
        self._writer.write_label(end_label)

    def compile_do(self):
        self.consume(TokenType.KEYWORD, "do")
        self._compile_subroutine_call()
        self.consume(TokenType.SYMBOL, ";")
        self._writer.write_pop("temp", 0)

    def compile_return(self):
        self.consume(TokenType.KEYWORD, "return")

        if self.check(TokenType.SYMBOL, ";"):
            self._writer.write_push("constant", 0)
        else:
            self.compile_expression()

        self.consume(TokenType.SYMBOL, ";")
        self._writer.write_return()

    def compile_expression(self):
        self.compile_term()

        while self.check(TokenType.SYMBOL) and self.peek().value in "+-*/&|<=>":
            operation = self.advance().value
            self.compile_term()
            self._write_operation(operation)

    def compile_term(self):
        token = self.peek()
        if token is None:
            raise ParserError("Expected term, found end of input", *self._eof_position())

        if self.match(TokenType.SYMBOL, "-"):
            self.compile_term()
            self._writer.write_arithmetic("neg")
        elif self.match(TokenType.SYMBOL, "~"):
            self.compile_term()
            self._writer.write_arithmetic("not")
        elif self.match(TokenType.SYMBOL, "("):
            self.compile_expression()
            self.consume(TokenType.SYMBOL, ")")
        elif self.check(TokenType.INTEGER_CONSTANT):
            value = int(self.advance().value)
            self._writer.write_push("constant", value)
        elif self.check(TokenType.STRING_CONSTANT):
            value = self.advance().value
            self._write_string_constant(value)
        elif self.check(TokenType.KEYWORD) and token.value in ("true", "false", "null", "this"):
            self._write_keyword_constant(self.advance().value)
        elif self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            if self.match(TokenType.SYMBOL, "["):
                self._write_push_symbol(name)
                self.compile_expression()
                self.consume(TokenType.SYMBOL, "]")
                self._writer.write_arithmetic("add")
                self._writer.write_pop("pointer", 1)
                self._writer.write_push("that", 0)
            elif self.check(TokenType.SYMBOL, "(") or self.check(TokenType.SYMBOL, "."):
                self._compile_subroutine_call_with_name(name)
            else:
                self._write_push_symbol(name)
        else:
            raise ParserError(f"Unexpected token in term: {token.value}", token.line, token.column)

    def compile_expression_list(self) -> int:
        if self.check(TokenType.SYMBOL, ")"):
            return 0

        count = 1
        self.compile_expression()
        while self.match(TokenType.SYMBOL, ","):
            self.compile_expression()
            count += 1
        return count

    def _compile_type(self) -> str:
        if self.check(TokenType.KEYWORD) and self.peek().value in ("int", "char", "boolean"):
            return self.advance().value
        if self.check(TokenType.IDENTIFIER):
            return self.advance().value

        token = self.peek()
        if token is None:
            line, column = self._eof_position()
            raise ParserError("Expected type, found end of input", line, column)
        raise ParserError(f"Expected type, found {token.value}", token.line, token.column)

    def _compile_return_type(self) -> str:
        if self.check(TokenType.KEYWORD, "void"):
            return self.advance().value
        return self._compile_type()

    def _compile_subroutine_call(self) -> int:
        name = self.consume(TokenType.IDENTIFIER, description="subroutine name").value
        return self._compile_subroutine_call_with_name(name)

    def _compile_subroutine_call_with_name(self, name: str) -> int:
        n_args = 0

        if self.match(TokenType.SYMBOL, "."):
            subroutine_name = self.consume(
                TokenType.IDENTIFIER,
                description="subroutine name",
            ).value
            symbol = self._resolve_symbol(name)
            if symbol is None:
                full_name = f"{name}.{subroutine_name}"
            else:
                self._write_push_symbol(name)
                full_name = f"{symbol.type}.{subroutine_name}"
                n_args = 1
        else:
            full_name = f"{self._class_name}.{name}"
            if self._current_subroutine_kind != "function":
                self._writer.write_push("pointer", 0)
                n_args = 1

        self.consume(TokenType.SYMBOL, "(")
        n_args += self.compile_expression_list()
        self.consume(TokenType.SYMBOL, ")")
        self._writer.write_call(full_name, n_args)
        return n_args

    def _write_operation(self, operation: str):
        if operation == "*":
            self._writer.write_call("Math.multiply", 2)
        elif operation == "/":
            self._writer.write_call("Math.divide", 2)
        else:
            self._writer.write_arithmetic(self.BINARY_OPERATIONS[operation])

    def _write_string_constant(self, value: str):
        self._writer.write_push("constant", len(value))
        self._writer.write_call("String.new", 1)
        for character in value:
            self._writer.write_push("constant", ord(character))
            self._writer.write_call("String.appendChar", 2)

    def _write_keyword_constant(self, value: str):
        if value in ("false", "null"):
            self._writer.write_push("constant", 0)
        elif value == "true":
            self._writer.write_push("constant", 0)
            self._writer.write_arithmetic("not")
        elif value == "this":
            self._writer.write_push("pointer", 0)

    def _start_subroutine(self, subroutine_kind: str):
        self._subroutine_scope = {}
        self._subroutine_counts = {"arg": 0, "var": 0}
        self._label_counts = {}
        self._current_subroutine_kind = subroutine_kind

    def _define(self, name: str, type_name: str, kind: str):
        if kind in ("static", "field"):
            index = self._class_counts[kind]
            self._class_counts[kind] += 1
            self._class_scope[name] = Symbol(type_name, kind, index)
        elif kind in ("arg", "var"):
            index = self._subroutine_counts[kind]
            self._subroutine_counts[kind] += 1
            self._subroutine_scope[name] = Symbol(type_name, kind, index)
        else:
            raise ValueError(f"Tipo de simbolo invalido: {kind}")

    def _resolve_symbol(self, name: str) -> Symbol | None:
        if name in self._subroutine_scope:
            return self._subroutine_scope[name]
        return self._class_scope.get(name)

    def _write_push_symbol(self, name: str):
        symbol = self._require_symbol(name)
        self._writer.write_push(self.KIND_TO_SEGMENT[symbol.kind], symbol.index)

    def _write_pop_symbol(self, name: str):
        symbol = self._require_symbol(name)
        self._writer.write_pop(self.KIND_TO_SEGMENT[symbol.kind], symbol.index)

    def _require_symbol(self, name: str) -> Symbol:
        symbol = self._resolve_symbol(name)
        if symbol is None:
            token = self.previous() or self.peek()
            if token is None:
                line, column = self._eof_position()
            else:
                line, column = token.line, token.column
            raise ParserError(f"Identificador nao declarado: {name}", line, column)
        return symbol

    def _next_label_index(self, prefix: str) -> int:
        index = self._label_counts.get(prefix, 0)
        self._label_counts[prefix] = index + 1
        return index

    def _eof_position(self) -> tuple[int, int]:
        previous = self.previous()
        if previous is None:
            return 1, 1
        return previous.line, previous.column + len(previous.value)

    def _describe_expected(self, token_type: TokenType, value: str | None) -> str:
        if value is None:
            return token_type.name
        return f"{token_type.name} {value!r}"


def compilar_codigo_jack(codigo_fonte: str) -> str:
    lexer = JackLexer(codigo_fonte)
    tokens = lexer.tokenize()
    compiler = JackVMCompiler(tokens)
    return compiler.compile()
