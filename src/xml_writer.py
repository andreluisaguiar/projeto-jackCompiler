
"""Módulo para escrita de arquivos XML no formato nand2tetris"""

from pathlib import Path

def escrever_xml(conteudo: str, caminho_saida: str):
    """
    Escreve o conteúdo XML em um arquivo.
    
    Args:
        conteudo: String com o conteúdo XML formatado
        caminho_saida: Caminho do arquivo de saída (.xml)
    """
    # Cria diretório pai se não existir
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    
    with open(caminho_saida, 'w', encoding='utf-8') as arquivo:
        arquivo.write(conteudo)
        arquivo.write('\n')  # Nova linha final conforme padrão oficial