# JackCompiler - Gerador de Código Intermediário VM

### Projeto da disciplina de Compiladores - Engenharia da Computação/UFMA

Compilador para a linguagem Jack, do projeto nand2tetris. O projeto agora integra scanner, parser, geração XML de validação e geração de código intermediário `.vm`, compatível com o VM Emulator oficial.

## Dupla

| Nome | Matrícula |
|------|-----------|
| André Luis Aguiar do Nascimento | 20250071151 |
| Virginia Maria Mondego Ferreira | 20250071349 |

## Linguagem utilizada

- Python 3.10+
- Sem dependências externas
- Testes com `unittest`

## Estrutura do projeto

```text
projeto-jackCompiler/
├── main.py
├── src/
│   ├── lexer.py          # Analisador léxico JackLexer
│   ├── parser.py         # Parser XML recursive descent
│   ├── processador.py    # Orquestra arquivo/diretório e saídas
│   ├── vm_compiler.py    # Gerador Jack -> VM
│   ├── vm_writer.py      # Escritor de comandos VM
│   └── xml_writer.py     # Escrita dos arquivos XML
├── tests/
│   ├── test_lexer.py
│   ├── test_parser_*.py
│   ├── test_processador.py
│   ├── test_vm_compiler.py
│   └── test_vm_writer.py
└── Square/
    ├── Main.jack
    ├── Square.jack
    └── SquareGame.jack
```

## Pipeline do compilador

O modo padrão gera código VM:

```text
arquivo .jack ou diretório
    ↓
JackLexer
    ↓
tokens Jack
    ↓
JackVMCompiler
    ↓
VMWriter
    ↓
arquivo .vm
```

Os modos de validação das entregas anteriores continuam disponíveis:

- `--xml`: gera XML sintático.
- `--tokens`: gera XML de tokens.

## Como executar

### Compilar arquivo único para VM

```bash
python3 main.py Main.jack
python3 main.py Square/Main.jack
```

Sem `--out`, o arquivo `.vm` é gerado ao lado do `.jack`:

```text
Square/Main.jack -> Square/Main.vm
```

### Compilar diretório inteiro para VM

```bash
python3 main.py ./projects/11/Square/
python3 main.py ./projects/11/Pong/
```

Ao receber uma pasta, o compilador procura arquivos `.jack` recursivamente e gera um `.vm` para cada classe.

### Usar diretório de saída configurável

```bash
python3 main.py ./projects/11/Pong/ --out output/project11
```

Com `--out`, a estrutura relativa da entrada é preservada dentro da pasta de saída.

### Gerar XML sintático

```bash
python3 main.py --xml Square/Main.jack output/Main.xml
```

### Gerar XML de tokens

```bash
python3 main.py --tokens Square/Main.jack output/MainT.xml
```

## Como validar

### Testes automatizados

```bash
python3 -m unittest discover -s tests -v
```

Os testes cobrem:

- lexer e parser XML já existentes;
- descoberta de arquivos `.jack` em diretórios;
- cálculo de saída `.vm`;
- comandos básicos do `VMWriter`;
- geração VM inicial para `do`, `return`, `let`, `if/else` e `while`.

### Validação incremental recomendada

Depois de extrair o pacote oficial do Project 11, valide nesta ordem:

```bash
python3 main.py ./projects/11/Seven/
python3 main.py ./projects/11/Average/
python3 main.py ./projects/11/ConvertToBin/
python3 main.py ./projects/11/ComplexArrays/
python3 main.py ./projects/11/Square/
python3 main.py ./projects/11/Pong/
```

Em seguida, carregue os arquivos `.vm` gerados no VM Emulator oficial.

Status atual:

- Testes automatizados locais: passando.
- Compilação de diretório testada com `Square/`: gera `Main.vm`, `Square.vm` e `SquareGame.vm`.
- Validação completa no VM Emulator com o pacote oficial Project 11: pendente quando os arquivos oficiais forem adicionados ao ambiente.

## Decisões técnicas

O projeto manteve o lexer e o parser XML das entregas anteriores para reduzir risco de regressão. A geração VM foi adicionada em uma nova compilation engine (`JackVMCompiler`), que reaproveita os tokens do `JackLexer` e emite comandos pelo `VMWriter`.

A entrada por diretório fica centralizada em `processador.py`, usando `Path.rglob("*.jack")` para compilação recursiva e ordenada. Isso permite compilar projetos com múltiplas classes, como `Square` e `Pong`, com um único comando.

Os rótulos de controle usam nomes previsíveis por subrotina:

```text
WHILE_EXP0
WHILE_END0
IF_TRUE0
IF_FALSE0
IF_END0
```

## Desafios enfrentados

O principal desafio foi evoluir o projeto de uma saída XML de validação para uma saída executável em VM sem quebrar os testes anteriores. Também foi necessário separar claramente os modos da CLI: VM por padrão, XML sintático com `--xml` e XML de tokens com `--tokens`.
