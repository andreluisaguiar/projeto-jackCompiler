"""Módulo que orquestra lexer e parser para arquivos Jack."""

from pathlib import Path
from src.lexer import JackLexer
from src.parser import JackParser
from src.xml_writer import escrever_xml


def _ler_codigo_fonte(caminho_entrada: str) -> str:
    with open(caminho_entrada, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()


def _tokenizar(codigo_fonte: str):
    lexer = JackLexer(codigo_fonte)
    tokens = lexer.tokenize()
    return lexer, tokens


def processar_arquivo_jack(caminho_entrada: str, caminho_saida: str = None):
    """
    Processa um arquivo .jack e gera o XML da árvore sintática.
    
    Args:
        caminho_entrada: Caminho para o arquivo .jack de entrada
        caminho_saida: Caminho para o arquivo .xml de saída (opcional)
                      Se None, usa convenção: Foo.jack → Foo.xml
    
    Returns:
        str: Caminho do arquivo XML gerado
    """
    codigo_fonte = _ler_codigo_fonte(caminho_entrada)
    _, tokens = _tokenizar(codigo_fonte)
    parser = JackParser(tokens)
    conteudo_xml = parser.parse()
    
    if caminho_saida is None:
        arquivo_entrada = Path(caminho_entrada)
        pasta_saida = Path("output")
        pasta_saida.mkdir(exist_ok=True)
        caminho_saida = pasta_saida / (arquivo_entrada.stem + '.xml')
    
    escrever_xml(conteudo_xml, caminho_saida)
    print(f"Gerado: {caminho_saida}")
    
    return str(caminho_saida)


def tokenizar_arquivo_jack(caminho_entrada: str, caminho_saida: str = None):
    """
    Gera o XML de tokens do scanner, útil para validar a primeira parte.
    Se caminho_saida for None, usa convenção: Foo.jack → FooT.xml.
    """
    codigo_fonte = _ler_codigo_fonte(caminho_entrada)
    lexer, _ = _tokenizar(codigo_fonte)
    conteudo_xml = lexer.to_xml()

    if caminho_saida is None:
        arquivo_entrada = Path(caminho_entrada)
        pasta_saida = Path("output")
        pasta_saida.mkdir(exist_ok=True)
        caminho_saida = pasta_saida / (arquivo_entrada.stem + 'T.xml')

    escrever_xml(conteudo_xml, caminho_saida)
    print(f"Gerado: {caminho_saida}")

    return str(caminho_saida)
