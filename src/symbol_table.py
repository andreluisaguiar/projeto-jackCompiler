"""Tabela de simbolos para o compilador Jack.

Gerencia dois escopos:
  - Escopo de classe: variaveis 'static' e 'field'
  - Escopo de subrotina: variaveis 'arg' e 'var' (local)

Cada simbolo possui: nome, tipo, categoria (kind) e indice unico por categoria.
"""

from dataclasses import dataclass
from typing import Optional


VALID_CLASS_KINDS = {"static", "field"}
VALID_SUBROUTINE_KINDS = {"arg", "var"}
VALID_KINDS = VALID_CLASS_KINDS | VALID_SUBROUTINE_KINDS

KIND_TO_SEGMENT = {
    "static": "static",
    "field": "this",
    "arg": "argument",
    "var": "local",
}


@dataclass
class Symbol:
    """Representa um simbolo na tabela com seu tipo, categoria e indice."""
    name: str
    type: str
    kind: str
    index: int

    def segment(self) -> str:
        """Retorna o segmento VM correspondente a este simbolo."""
        return KIND_TO_SEGMENT[self.kind]


class SymbolTable:
    """Tabela de simbolos de dois escopos para a linguagem Jack."""

    def __init__(self):
        self._class_scope: dict[str, Symbol] = {}
        self._subroutine_scope: dict[str, Symbol] = {}
        self._class_counts: dict[str, int] = {"static": 0, "field": 0}
        self._subroutine_counts: dict[str, int] = {"arg": 0, "var": 0}

    def start_subroutine(self):
        """Inicia um novo escopo de subrotina, descartando o anterior."""
        self._subroutine_scope = {}
        self._subroutine_counts = {"arg": 0, "var": 0}

    def define(self, name: str, type_name: str, kind: str) -> Symbol:
        """Define um novo simbolo no escopo apropriado."""
        if kind not in VALID_KINDS:
            raise ValueError(f"Categoria invalida: {kind!r}. Esperado: {sorted(VALID_KINDS)}")
        if not name or not isinstance(name, str):
            raise ValueError(f"Nome de simbolo invalido: {name!r}")
        if not type_name or not isinstance(type_name, str):
            raise ValueError(f"Tipo invalido: {type_name!r}")

        if kind in VALID_CLASS_KINDS:
            index = self._class_counts[kind]
            self._class_counts[kind] += 1
            symbol = Symbol(name=name, type=type_name, kind=kind, index=index)
            self._class_scope[name] = symbol
        else:
            index = self._subroutine_counts[kind]
            self._subroutine_counts[kind] += 1
            symbol = Symbol(name=name, type=type_name, kind=kind, index=index)
            self._subroutine_scope[name] = symbol

        return symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca um simbolo pelo nome nos dois escopos (subrotina tem prioridade)."""
        if name in self._subroutine_scope:
            return self._subroutine_scope[name]
        return self._class_scope.get(name)

    def contains(self, name: str) -> bool:
        return self.lookup(name) is not None

    def type_of(self, name: str) -> Optional[str]:
        sym = self.lookup(name)
        return sym.type if sym else None

    def kind_of(self, name: str) -> Optional[str]:
        sym = self.lookup(name)
        return sym.kind if sym else None

    def index_of(self, name: str) -> Optional[int]:
        sym = self.lookup(name)
        return sym.index if sym else None

    def segment_of(self, name: str) -> Optional[str]:
        sym = self.lookup(name)
        return sym.segment() if sym else None

    def var_count(self, kind: str) -> int:
        if kind in VALID_CLASS_KINDS:
            return self._class_counts[kind]
        if kind in VALID_SUBROUTINE_KINDS:
            return self._subroutine_counts[kind]
        raise ValueError(f"Categoria invalida: {kind!r}")

    def __repr__(self) -> str:
        return f"SymbolTable(class={list(self._class_scope.keys())}, subroutine={list(self._subroutine_scope.keys())})"