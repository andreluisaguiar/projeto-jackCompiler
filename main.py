"""Ponto de entrada do compilador Jack."""

import sys
from src.processador import processar_arquivo_jack, tokenizar_arquivo_jack


def mostrar_uso():
    print("Uso: python3 main.py [--tokens] <arquivo.jack> [saida.xml]")
    print("Exemplos:")
    print("  python3 main.py Square/Main.jack")
    print("  python3 main.py Square/Main.jack output/Main.xml")
    print("  python3 main.py --tokens Square/Main.jack output/MainT.xml")


def principal():
    """Função principal do programa"""

    argumentos = sys.argv[1:]
    if not argumentos:
        mostrar_uso()
        sys.exit(1)

    gerar_tokens = argumentos[0] == "--tokens"
    if gerar_tokens:
        argumentos = argumentos[1:]

    if not argumentos:
        mostrar_uso()
        sys.exit(1)
    
    arquivo_entrada = argumentos[0]
    arquivo_saida = argumentos[1] if len(argumentos) > 1 else None
    
    try:
        if gerar_tokens:
            tokenizar_arquivo_jack(arquivo_entrada, arquivo_saida)
            print("Tokenização concluída com sucesso!")
        else:
            processar_arquivo_jack(arquivo_entrada, arquivo_saida)
            print("Análise sintática concluída com sucesso!")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
        
    except Exception as erro:
        print(f"Erro durante o processamento: {erro}")
        sys.exit(1)

if __name__ == "__main__":
    principal()
