"""Ponto de entrada do compilador Jack - Analisador Léxico (Tokenizer)"""

import sys
from pathlib import Path
from src.processador import processar_arquivo_jack

def principal():
    """Função principal do programa"""
    
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.jack> [saida.xml]")
        print("Exemplos:")
        print("  python main.py Square/Square.jack")
        print("  python main.py Main.jack output/MainT.xml")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        processar_arquivo_jack(arquivo_entrada, arquivo_saida)
        print("Tokenização concluída com sucesso!")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
        
    except Exception as erro:
        print(f"Erro durante a tokenização: {erro}")
        sys.exit(1)

if __name__ == "__main__":
    principal()