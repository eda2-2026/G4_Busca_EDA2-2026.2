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


def busca_sequencial(
    vagas: List[Dict[str, Any]],
    termo: str,
    campo: str = "titulo",
) -> Tuple[List[Dict[str, Any]], int]:
    termo_normalizado = _normalizar(termo)
    resultados: List[Dict[str, Any]] = []
    comparacoes = 0

    indice = 0
    total = len(vagas)

    while indice < total:
        vaga = vagas[indice]
        valor_campo = _normalizar(str(vaga.get(campo, "")))

        comparacoes += 1

        if _comeca_com(valor_campo, termo_normalizado):
            resultados.append(vaga)

        indice += 1

    return resultados, comparacoes


def busca_sequencial_exata(
    vagas: List[Dict[str, Any]],
    termo: str,
    campo: str = "titulo",
) -> Tuple[Optional[Dict[str, Any]], int]:
    termo_normalizado = _normalizar(termo)
    comparacoes = 0

    indice = 0
    total = len(vagas)

    while indice < total:
        vaga = vagas[indice]
        valor_campo = _normalizar(str(vaga.get(campo, "")))

        comparacoes += 1

        if valor_campo == termo_normalizado:
            return vaga, comparacoes

        indice += 1

    return None, comparacoes