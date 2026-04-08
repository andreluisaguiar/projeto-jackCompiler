# JackCompiler - Analisador Léxico (Tokenizer)

### Projeto do módulo I da disciplina de Compiladores - Engenharia da Computação/UFMA

Implementação do scanner para a linguagem Jack (projeto nand2tetris)

## Dupla

| Nome | Matrícula |
|------|-----------|
| André Luis Aguiar do Nascimento | 20250071151 |
| Virginia Maria Mondego Ferreira | 20250071349 |

---

## Linguagem utilizada

- **Python 3.10+**
- Sem dependências externas (biblioteca padrão apenas)

---

## Estrutura do Projeto

projeto-jackCompiler/
```
├── main.py 
├── src/
│ ├── init.py
│ ├── lexer.py # Analisador léxico (JackLexer)
│ ├── processador.py 
│ └── xml_writer.py # Escritor de arquivos XML
├── testes/
│ ├── init.py
│ └── test_lexer.py # Testes unitários
├── Square/ # Arquivos oficiais do nand2tetris 
│ ├── Main.jack, Square.jack, SquareGame.jack
│ └── *T.xml (gabaritos oficiais)
├── output/ # Saída gerada pelo tokenizer
└── README.md
```

---
## Como executar

### Pré-requisitos

- Python 3.8 ou superior instalado
- Terminal (PowerShell, CMD ou Bash)

### Passo a passo

1. Clone ou baixe o projeto:
   ```bash
   git clone <https://github.com/andreluisaguiar/projeto-jackCompiler.git>
   cd projeto-jackCompiler
2. Execute o tokenizer:
    ```bash
    # Tokenizar um único arquivo (saída automática em output/)
    python main.py Square/Main.jack
    # Tokenizar os demais: 
    python main.py Square/Square.jack
    python main.py Square/SquareGame.jack
3. Os arquivos gerados serão salvos em output/:
    ```
    output/
    ├── MainT.xml
    ├── SquareT.xml
    └── SquareGameT.xml
    ```
---
## Como validar
### Comparação com arquivos oficiais (Windows/PowerShell)

**Comparar Main**:
```
fc.exe /L Square\MainT.xml output\MainT.xml
```
**Comparar Square**
```
fc.exe /L Square\SquareT.xml output\SquareT.xml
```
**Comparar SquareGame**
```
fc.exe /L Square\SquareGameT.xml output\SquareGameT.xml
```
*Se aparecer: "FC: não foram encontradas diferenças" → Validado!*

---
## Rodar testes unitários do lexico:
```
python -m unittest tests/test_lexer.py -v
```
## Rodar teste para tokenização com saída em xml:
```
python main.py tests/teste.jack
```