"""Ponto de entrada do compilador Jack."""

import argparse
import sys
from pathlib import Path

from src.processador import compilar_entrada, processar_arquivo_jack, tokenizar_arquivo_jack


def mostrar_uso():
    print("Uso: python3 main.py [--xml | --tokens] [--out DIR] <arquivo.jack|diretorio> [saida]")
    print("Exemplos:")
    print("  python3 main.py Square/")
    print("  python3 main.py Square/Main.jack")
    print("  python3 main.py Square/ --out output/vm")
    print("  python3 main.py --xml Square/Main.jack output/Main.xml")
    print("  python3 main.py --tokens Square/Main.jack output/MainT.xml")


def criar_parser_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 main.py",
        description="Compilador Jack: gera VM por padrao e preserva XML via flags.",
    )
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--xml", action="store_true", help="gera XML sintatico")
    modos.add_argument("--tokens", action="store_true", help="gera XML de tokens")
    parser.add_argument("--out", dest="pasta_saida", help="diretorio de saida para arquivos .vm")
    parser.add_argument("entrada", nargs="?", help="arquivo .jack ou diretorio")
    parser.add_argument("saida", nargs="?", help="arquivo de saida XML/Tokens para compatibilidade")
    return parser


def _saida_xml_por_out(entrada: str, pasta_saida: str | None, sufixo: str) -> str | None:
    if pasta_saida is None:
        return None
    arquivo = Path(entrada)
    return str(Path(pasta_saida) / f"{arquivo.stem}{sufixo}")


def principal():
    """Função principal do programa"""
    parser = criar_parser_argumentos()
    args = parser.parse_args()

    if not args.entrada:
        mostrar_uso()
        sys.exit(1)
    
    try:
        if args.tokens:
            caminho_saida = args.saida or _saida_xml_por_out(args.entrada, args.pasta_saida, "T.xml")
            tokenizar_arquivo_jack(args.entrada, caminho_saida)
            print("Tokenização concluída com sucesso!")
        elif args.xml:
            caminho_saida = args.saida or _saida_xml_por_out(args.entrada, args.pasta_saida, ".xml")
            processar_arquivo_jack(args.entrada, caminho_saida)
            print("Análise sintática concluída com sucesso!")
        else:
            compilar_entrada(args.entrada, args.pasta_saida)
            print("Compilação VM concluída com sucesso!")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {args.entrada}")
        sys.exit(1)
        
    except Exception as erro:
        print(f"Erro durante o processamento: {erro}")
        sys.exit(1)

if __name__ == "__main__":
    principal()
