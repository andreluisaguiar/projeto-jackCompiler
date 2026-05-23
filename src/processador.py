"""Módulo que orquestra lexer e parser para arquivos Jack."""

from pathlib import Path
from src.lexer import JackLexer
from src.parser import JackParser
from src.vm_compiler import compilar_codigo_jack
from src.xml_writer import escrever_xml


def resolver_arquivos_jack(caminho_entrada: str) -> list[Path]:
    """
    Resolve uma entrada do compilador para uma lista ordenada de arquivos .jack.

    A entrada pode ser um arquivo unico ou um diretorio. Diretorios sao lidos de
    forma recursiva para permitir projetos com subpastas.
    """
    entrada = Path(caminho_entrada)

    if entrada.is_file():
        if entrada.suffix.lower() != ".jack":
            raise ValueError(f"Arquivo de entrada nao e .jack: {entrada}")
        return [entrada]

    if entrada.is_dir():
        arquivos = sorted(entrada.rglob("*.jack"))
        if not arquivos:
            raise ValueError(f"Nenhum arquivo .jack encontrado em: {entrada}")
        return arquivos

    raise FileNotFoundError(caminho_entrada)


def calcular_caminho_saida_vm(
    arquivo_jack: str | Path,
    raiz_entrada: str | Path | None = None,
    pasta_saida: str | Path | None = None,
) -> Path:
    """
    Calcula o caminho .vm de saida para um arquivo .jack.

    Sem pasta_saida, o .vm fica ao lado do .jack. Com pasta_saida, preserva a
    estrutura relativa quando a entrada original for um diretorio.
    """
    arquivo = Path(arquivo_jack)

    if pasta_saida is None:
        return arquivo.with_suffix(".vm")

    base_saida = Path(pasta_saida)
    if raiz_entrada is None:
        relativo = Path(arquivo.name)
    else:
        raiz = Path(raiz_entrada)
        if raiz.is_file():
            relativo = Path(arquivo.name)
        else:
            relativo = arquivo.relative_to(raiz)

    return base_saida / relativo.with_suffix(".vm")


def _ler_codigo_fonte(caminho_entrada: str) -> str:
    with open(caminho_entrada, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()


def _tokenizar(codigo_fonte: str):
    lexer = JackLexer(codigo_fonte)
    tokens = lexer.tokenize()
    return lexer, tokens


def compilar_arquivo_jack(caminho_entrada: str, caminho_saida: str | Path | None = None):
    """
    Compila um arquivo .jack e gera codigo VM.

    Se caminho_saida for None, usa a convencao Foo.jack -> Foo.vm ao lado do
    arquivo de entrada.
    """
    codigo_fonte = _ler_codigo_fonte(caminho_entrada)
    conteudo_vm = compilar_codigo_jack(codigo_fonte)

    if caminho_saida is None:
        caminho_saida = calcular_caminho_saida_vm(caminho_entrada)

    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    conteudo = conteudo_vm
    if conteudo:
        conteudo += "\n"
    caminho_saida.write_text(conteudo, encoding="utf-8")
    print(f"Gerado: {caminho_saida}")

    return str(caminho_saida)


def compilar_entrada(caminho_entrada: str, pasta_saida: str | Path | None = None) -> list[str]:
    """
    Compila uma entrada que pode ser arquivo .jack ou diretorio com arquivos .jack.
    """
    arquivos = resolver_arquivos_jack(caminho_entrada)
    raiz = Path(caminho_entrada)
    caminhos_gerados = []

    for arquivo in arquivos:
        caminho_saida = calcular_caminho_saida_vm(arquivo, raiz, pasta_saida)
        caminhos_gerados.append(compilar_arquivo_jack(str(arquivo), caminho_saida))

    return caminhos_gerados


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
