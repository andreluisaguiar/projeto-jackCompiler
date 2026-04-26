# JackCompiler - Scanner e Parser Jack

### Projeto do módulo I da disciplina de Compiladores - Engenharia da Computação/UFMA

Implementação do analisador léxico e do analisador sintático para a linguagem Jack, do projeto nand2tetris.

## Dupla

| Nome | Matrícula |
|------|-----------|
| André Luis Aguiar do Nascimento | 20250071151 |
| Virginia Maria Mondego Ferreira | 20250071349 |

---

## Linguagem utilizada

- Python 3.10+
- Sem dependências externas

---

## Estrutura do projeto

```text
projeto-jackCompiler/
├── main.py
├── src/
│   ├── __init__.py
│   ├── lexer.py          # Analisador léxico JackLexer
│   ├── parser.py         # Parser recursive descent JackParser
│   ├── processador.py    # Integra lexer + parser
│   └── xml_writer.py     # Escrita dos arquivos XML
├── tests/
│   ├── test_lexer.py
│   ├── test_parser_helpers.py
│   ├── test_parser_erro.py
│   ├── test_parser_of.py
│   └── test_processador.py
├── Square/
│   ├── Main.jack, Square.jack, SquareGame.jack
│   ├── Main.xml, Square.xml, SquareGame.xml
│   └── MainT.xml, SquareT.xml, SquareGameT.xml
└── output/
```

---

## Como executar

### Gerar XML sintático do parser

Por padrão, o programa executa scanner + parser e gera a árvore sintática.

```bash
python3 main.py Square/Main.jack
python3 main.py Square/Square.jack
python3 main.py Square/SquareGame.jack
```

Os arquivos gerados serão salvos em `output/`:

```text
output/Main.xml
output/Square.xml
output/SquareGame.xml
```

Também é possível informar o caminho de saída:

```bash
python3 main.py Square/Main.jack output/Main.xml
```

Nome do arquivo de saída XML do parser: `NomeDoArquivo.xml`.

### Gerar XML de tokens do scanner

Para validar apenas o analisador léxico, use `--tokens`:

```bash
python3 main.py --tokens Square/Main.jack output/MainT.xml
```

Nome do arquivo de saída XML do scanner: `NomeDoArquivoT.xml`.

---

## Como validar

### Testes automatizados

```bash
python3 -m unittest discover -s tests -v
```

Os testes comparam a saída sintática gerada com os XMLs oficiais:

- `Square/Main.jack` → `Square/Main.xml`
- `Square/Square.jack` → `Square/Square.xml`
- `Square/SquareGame.jack` → `Square/SquareGame.xml`

Status atual da validação: os três arquivos oficiais passam nos testes automatizados.

### Comparação manual

```bash
python3 main.py Square/Main.jack output/Main.xml
diff -w Square/Main.xml output/Main.xml
```

No Windows/PowerShell:

```powershell
python main.py Square/Main.jack output/Main.xml
fc.exe /L Square\Main.xml output\Main.xml
```

---

## Decisões técnicas

O parser foi implementado com recursive descent, usando um método `compile_*` para cada não-terminal relevante da gramática Jack. O lexer foi mantido como etapa inicial do fluxo e agora os tokens carregam linha e coluna, permitindo mensagens de erro sintático mais claras.

A geração XML segue a estrutura esperada pelo nand2tetris. Um cuidado importante foi escrever no XML todos os símbolos consumidos durante o parsing, como `.`, `[`, `]`, `(`, `)`, `,` e os operadores. Outro ponto de atenção foi o `else`, que no XML oficial aparece como keyword dentro de `ifStatement`, sem uma tag extra.

## Desafios enfrentados

Os principais desafios foram integrar o parser sem quebrar o scanner já existente, reproduzir exatamente a hierarquia XML oficial e identificar diferenças sutis causadas por tokens consumidos sem escrita no XML. Também foi necessário separar a saída de tokens (`T.xml`) da saída sintática (`.xml`) para manter as duas validações disponíveis.
