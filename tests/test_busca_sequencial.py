import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from busca.busca_sequencial import busca_sequencial, busca_sequencial_exata


def _vaga(id_, titulo):
    return {
        "id": id_,
        "titulo": titulo,
        "empresa": "Empresa Teste",
        "localizacao": "Brasília",
        "descricao": "Descrição de teste.",
        "url": "https://exemplo.invalido",
    }


VAGAS_EXEMPLO = [
    _vaga(1, "Analista de Dados"),
    _vaga(2, "Analista de Sistemas"),
    _vaga(3, "Desenvolvedor Backend"),
    _vaga(4, "Desenvolvedor Frontend"),
    _vaga(5, "Engenheiro de Software"),
]


def test_elemento_existe():
    resultados, comparacoes = busca_sequencial(VAGAS_EXEMPLO, "Desenvolvedor Backend")
    assert len(resultados) == 1
    assert resultados[0]["id"] == 3
    assert comparacoes == len(VAGAS_EXEMPLO)


def test_elemento_nao_existe():
    resultados, comparacoes = busca_sequencial(VAGAS_EXEMPLO, "Cientista de Dados")
    assert resultados == []
    assert comparacoes == len(VAGAS_EXEMPLO)  # percorreu tudo


def test_lista_com_apenas_um_elemento():
    unica = [_vaga(1, "Desenvolvedor Backend")]

    resultados, comparacoes = busca_sequencial(unica, "Desenvolvedor Backend")
    assert len(resultados) == 1
    assert comparacoes == 1

    resultados, comparacoes = busca_sequencial(unica, "Analista")
    assert resultados == []
    assert comparacoes == 1


def test_lista_vazia():
    resultados, comparacoes = busca_sequencial([], "Desenvolvedor")
    assert resultados == []
    assert comparacoes == 0


def test_elementos_repetidos():
    vagas_repetidas = VAGAS_EXEMPLO + [_vaga(6, "Desenvolvedor Backend")]
    resultados, comparacoes = busca_sequencial(vagas_repetidas, "Desenvolvedor Backend")
    assert len(resultados) == 2
    assert comparacoes == len(vagas_repetidas)


def test_busca_prefixo_encontra_multiplas_vagas():
    resultados, _ = busca_sequencial(VAGAS_EXEMPLO, "Desenvolvedor")
    titulos = {vaga["titulo"] for vaga in resultados}
    assert titulos == {"Desenvolvedor Backend", "Desenvolvedor Frontend"}


def test_busca_case_insensitive():
    resultados, _ = busca_sequencial(VAGAS_EXEMPLO, "desenvolvedor backend")
    assert len(resultados) == 1
    assert resultados[0]["id"] == 3


def test_busca_sequencial_exata_encontra():
    vaga, comparacoes = busca_sequencial_exata(VAGAS_EXEMPLO, "Engenheiro de Software")
    assert vaga is not None
    assert vaga["id"] == 5
    assert comparacoes == 5


def test_busca_sequencial_exata_nao_encontra():
    vaga, comparacoes = busca_sequencial_exata(VAGAS_EXEMPLO, "Vaga Inexistente")
    assert vaga is None
    assert comparacoes == len(VAGAS_EXEMPLO)
