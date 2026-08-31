from typing import List, Dict, Any, Tuple, Optional


def _normalizar(texto: str) -> str:
    return texto.strip().lower()


def _comeca_com(valor: str, termo: str) -> bool:
    if len(termo) > len(valor):
        return False
    posicao = 0
    while posicao < len(termo):
        if valor[posicao] != termo[posicao]:
            return False
        posicao += 1
    return True


class _ContadorComparacoes:

    def __init__(self):
        self.total = 0

    def incrementar(self):
        self.total += 1


def _limite_inferior(
    vagas: List[Dict[str, Any]],
    termo: str,
    campo: str,
    contador: _ContadorComparacoes,
) -> int:
    esquerda = 0
    direita = len(vagas)

    while esquerda < direita:
        meio = (esquerda + direita) // 2
        valor_meio = _normalizar(str(vagas[meio].get(campo, "")))

        contador.incrementar()

        if valor_meio < termo:
            esquerda = meio + 1
        else:
            direita = meio

    return esquerda


def _limite_superior(
    vagas: List[Dict[str, Any]],
    termo_prefixo_seguinte: str,
    campo: str,
    contador: _ContadorComparacoes,
) -> int:
    esquerda = 0
    direita = len(vagas)

    while esquerda < direita:
        meio = (esquerda + direita) // 2
        valor_meio = _normalizar(str(vagas[meio].get(campo, "")))

        contador.incrementar()

        if valor_meio < termo_prefixo_seguinte:
            esquerda = meio + 1
        else:
            direita = meio

    return esquerda


def _proximo_prefixo(termo: str) -> str:
    if not termo:
        return termo

    caracteres = list(termo)
    ultimo = caracteres[-1]
    caracteres[-1] = chr(ord(ultimo) + 1)
    return "".join(caracteres)


def busca_binaria(
    vagas_ordenadas: List[Dict[str, Any]],
    termo: str,
    campo: str = "titulo",
) -> Tuple[List[Dict[str, Any]], int]:
    termo_normalizado = _normalizar(termo)
    contador = _ContadorComparacoes()

    inicio = _limite_inferior(vagas_ordenadas, termo_normalizado, campo, contador)
    fim = _limite_superior(
        vagas_ordenadas, _proximo_prefixo(termo_normalizado), campo, contador
    )

    resultados = vagas_ordenadas[inicio:fim]

    return resultados, contador.total


def busca_binaria_exata(
    vagas_ordenadas: List[Dict[str, Any]],
    termo: str,
    campo: str = "titulo",
) -> Tuple[Optional[Dict[str, Any]], int]:
    termo_normalizado = _normalizar(termo)
    comparacoes = 0

    esquerda = 0
    direita = len(vagas_ordenadas) - 1

    while esquerda <= direita:
        meio = (esquerda + direita) // 2
        valor_meio = _normalizar(str(vagas_ordenadas[meio].get(campo, "")))

        comparacoes += 1

        if valor_meio == termo_normalizado:
            return vagas_ordenadas[meio], comparacoes
        elif valor_meio < termo_normalizado:
            esquerda = meio + 1
        else:
            direita = meio - 1

    return None, comparacoes