"""
Preprocessador: remove comentários do código-fonte Jack
antes de enviar ao tokenizador.
"""
"""Módulo que orquestra o processo de tokenização: lê .jack → tokeniza → escreve .xml"""

from pathlib import Path
from src.lexer import JackLexer
from src.xml_writer import escrever_xml

def processar_arquivo_jack(caminho_entrada: str, caminho_saida: str = None):
    """
    Processa um arquivo .jack e gera o arquivo XML correspondente.
    
    Args:
        caminho_entrada: Caminho para o arquivo .jack de entrada
        caminho_saida: Caminho para o arquivo .xml de saída (opcional)
                      Se None, usa convenção: Foo.jack → FooT.xml
    
    Returns:
        str: Caminho do arquivo XML gerado
    """
    # Lê o arquivo fonte com encoding UTF-8
    with open(caminho_entrada, 'r', encoding='utf-8') as arquivo:
        codigo_fonte = arquivo.read()
    
    # Cria o lexer e tokeniza o código
    lexer = JackLexer(codigo_fonte)
    lexer.tokenize()
    
    # Gera o conteúdo XML
    conteudo_xml = lexer.to_xml()
    
    # Define caminho de saída se não foi fornecido
    if caminho_saida is None:
        arquivo_entrada = Path(caminho_entrada)
        # Salva na pasta output/ para não sobrescrever os oficiais
        pasta_saida = Path("output")
        pasta_saida.mkdir(exist_ok=True)
        caminho_saida = pasta_saida / (arquivo_entrada.stem + 'T.xml')
    
    # Escreve o arquivo de saída
    escrever_xml(conteudo_xml, caminho_saida)
    print(f"Gerado: {caminho_saida}")
    
    return caminho_saida