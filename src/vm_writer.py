"""Escritor de comandos da VM do nand2tetris."""

from pathlib import Path


class VMWriter:
    """Acumula comandos VM em memoria e salva em arquivo quando necessario."""

    SEGMENTS = {
        "constant",
        "argument",
        "local",
        "static",
        "this",
        "that",
        "pointer",
        "temp",
    }

    ARITHMETIC_COMMANDS = {
        "add",
        "sub",
        "neg",
        "eq",
        "gt",
        "lt",
        "and",
        "or",
        "not",
    }

    def __init__(self):
        self._lines: list[str] = []

    def write_push(self, segment: str, index: int):
        self._validate_segment(segment)
        self._validate_index(index)
        self._write(f"push {segment} {index}")

    def write_pop(self, segment: str, index: int):
        self._validate_segment(segment)
        if segment == "constant":
            raise ValueError("Nao e possivel usar pop no segmento constant")
        self._validate_index(index)
        self._write(f"pop {segment} {index}")

    def write_arithmetic(self, command: str):
        if command not in self.ARITHMETIC_COMMANDS:
            raise ValueError(f"Comando aritmetico invalido: {command}")
        self._write(command)

    def write_label(self, label: str):
        self._write(f"label {label}")

    def write_goto(self, label: str):
        self._write(f"goto {label}")

    def write_if(self, label: str):
        self._write(f"if-goto {label}")

    def write_call(self, name: str, n_args: int):
        self._validate_index(n_args)
        self._write(f"call {name} {n_args}")

    def write_function(self, name: str, n_locals: int):
        self._validate_index(n_locals)
        self._write(f"function {name} {n_locals}")

    def write_return(self):
        self._write("return")

    def output(self) -> str:
        return "\n".join(self._lines)

    def save(self, path: str | Path):
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.output()
        if content:
            content += "\n"
        output_path.write_text(content, encoding="utf-8")

    def _write(self, command: str):
        self._lines.append(command)

    def _validate_segment(self, segment: str):
        if segment not in self.SEGMENTS:
            raise ValueError(f"Segmento VM invalido: {segment}")

    def _validate_index(self, index: int):
        if not isinstance(index, int) or index < 0:
            raise ValueError(f"Indice VM invalido: {index}")
